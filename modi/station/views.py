from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import get_recommended_candidates, fetch_all_travel_times, recommend_top_stations
from origin.models import Origin, Appointment
from .models import RecommendedStation
from django.shortcuts import get_object_or_404
from django.db import transaction

import logging
import time

logger = logging.getLogger(__name__)


def serialize_station(item):
    """RecommendedStation 모델 인스턴스 -> dict 변환 (공통 함수로 분리)"""
    return {
        "place_num": item.place_num,
        "station": item.station_name,
        "lines": item.lines,
        "average_time": item.average_time,
        "is_recommended": item.is_recommended,
        "participants": item.participants,
    }


class StationCandidateView(APIView):
    def get(self, request, appointment_code):
        logger.info(f"[GET] 추천 역 조회 시작 - 약속 코드: {appointment_code}")
        appointment = get_object_or_404(Appointment, appointment_code=appointment_code)
        saved_recommendations = RecommendedStation.objects.filter(appointment=appointment)

        if not saved_recommendations.exists():
            logger.warning(f"[GET] 추천 결과 없음 - 약속 코드: {appointment_code}")
            return Response({"error": "추천 결과가 아직 생성되지 않았습니다"}, status=status.HTTP_404_NOT_FOUND)
        logger.info(f"[GET] 추천 역 데이터 {saved_recommendations.count()}건 조회 성공 - 약속 코드: {appointment_code}")

        response_data = [serialize_station(item) for item in saved_recommendations]

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, appointment_code):
        logger.info(f"[POST] 추천 역 계산 및 저장 요청 시작 - 약속 코드: {appointment_code}")
        start_time = time.time()
        appointment = get_object_or_404(Appointment, appointment_code=appointment_code)
        origins = Origin.objects.filter(appointment=appointment)

        if appointment.status == Appointment.Status.COMPLETED:
            logger.warning(f"[POST] 이미 추천이 완료된 약속입니다 - 약속 코드: {appointment_code}")
            return Response(
                {"error": "이미 추천이 완료된 약속입니다."},
                status=status.HTTP_409_CONFLICT,
            )

        # 좌표 변환 (None/잘못된 값이 있으면 400 처리)
        try:
            participants_coords = [
                {"name": origin.name, "lat": float(origin.latitude), "lng": float(origin.longitude)}
                for origin in origins
            ]
        except (TypeError, ValueError):
            logger.error(f"[POST] 좌표 변환 실패 - 약속 코드: {appointment_code}")
            return Response(
                {"error": "참여자 좌표 데이터가 올바르지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(f"[POST] 조회된 참여자 수: {len(participants_coords)}명")

        if not participants_coords:
            logger.warning(f"[POST] 처리 중단: 참여자 좌표 데이터가 없습니다. - 약속 코드: {appointment_code}")
            return Response({"error": "참여자 좌표 데이터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 후보 역 조회 (외부/내부 서비스 호출 예외 처리)
        logger.info("[POST] 서비스 호출: get_recommended_candidates 시작")
        try:
            candidates = get_recommended_candidates(participants_coords)
            candidate_list = candidates.get("candidates", []) if isinstance(candidates, dict) else candidates
        except Exception as e:
            logger.error(f"[POST] 후보 역 조회 중 오류 - 약속 코드: {appointment_code}, 에러: {e}")
            return Response(
                {"error": "후보 역 조회 중 오류가 발생했습니다."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        logger.info(f"[POST] 추출된 후보 역 개수: {len(candidate_list)}개")

        # 후보 역이 없는 경우: appointment_id만 채운 빈 레코드 저장
        if not candidate_list:
            logger.warning(f"[POST] 후보 역이 없어 빈 레코드로 저장 - 약속 코드: {appointment_code}")
            with transaction.atomic():
                empty_station = RecommendedStation.objects.create(
                    appointment=appointment,
                    place_num=None,
                    station_name=None,
                    lines=None,
                    average_time=None,
                    is_recommended=None,
                    participants=None,
                )
                appointment.status = Appointment.Status.COMPLETED
                appointment.save(update_fields=["status"])

            total_elapsed = time.time() - start_time
            logger.info(f"[POST] 후보 없음으로 종료 (총 소요시간: {total_elapsed:.2f}초)")
            response_data = [serialize_station(empty_station)]
            return Response(response_data, status=status.HTTP_200_OK)

        # 대중교통 이동시간 조회 (외부 API 호출 예외 처리)
        logger.info("[POST] 서비스 호출: fetch_all_travel_times 시작 (외부 API 연동으로 시간이 걸릴 수 있음)")
        api_start = time.time()
        try:
            travel_times = fetch_all_travel_times(candidate_list, participants_coords)
        except Exception as e:
            logger.error(f"[POST] 이동시간 조회 중 오류 - 약속 코드: {appointment_code}, 에러: {e}")
            return Response(
                {"error": "이동시간 조회 중 오류가 발생했습니다."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        logger.info(f"[POST] 대중교통 이동시간 추출 완료 (소요시간: {time.time() - api_start:.2f}초)")

        # 추천 알고리즘 계산 (예외 처리)
        logger.info("[POST] 서비스 호출: recommend_top_stations 시작")
        try:
            result = recommend_top_stations(candidate_list, travel_times)
        except Exception as e:
            logger.error(f"[POST] 추천 계산 중 오류 - 약속 코드: {appointment_code}, 에러: {e}")
            return Response(
                {"error": "추천 계산 중 오류가 발생했습니다."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        logger.info(f"[POST] 최적의 알고리즘 계산 완료 (추천 대상 개수: {len(result)}개)")

        # 계산 결과가 비어있는 경우도 안전하게 처리
        if not result:
            logger.warning(f"[POST] 추천 결과가 비어있어 빈 레코드로 저장 - 약속 코드: {appointment_code}")
            with transaction.atomic():
                empty_station = RecommendedStation.objects.create(
                    appointment=appointment,
                    place_num=None,
                    station_name=None,
                    lines=None,
                    average_time=None,
                    is_recommended=None,
                    participants=None,
                )
                appointment.status = Appointment.Status.COMPLETED
                appointment.save(update_fields=["status"])

            total_elapsed = time.time() - start_time
            logger.info(f"[POST] 추천 결과 없음으로 종료 (총 소요시간: {total_elapsed:.2f}초)")
            response_data = [serialize_station(empty_station)]
            return Response(response_data, status=status.HTTP_200_OK)

        # result(계산 결과)를 새 객체로 저장 (필수 key 누락 방어)
        try:
            with transaction.atomic():
                new_stations = [
                    RecommendedStation(
                        appointment=appointment,
                        place_num=item.get("place_num"),
                        station_name=item.get("station"),
                        lines=item.get("lines"),
                        average_time=item.get("average_time"),
                        is_recommended=item.get("is_recommended", False),
                        participants=item.get("participants"),
                    )
                    for item in result
                ]
                created_stations = RecommendedStation.objects.bulk_create(new_stations)
                logger.info(
                    f"[POST] bulk_create 직후 개수: "
                    f"{RecommendedStation.objects.filter(appointment=appointment).count()}"
                )

                appointment.status = Appointment.Status.COMPLETED
                appointment.save(update_fields=["status"])
        except Exception as e:
            logger.error(f"[POST] 저장 중 오류 - 약속 코드: {appointment_code}, 에러: {e}")
            return Response(
                {"error": "추천 결과 저장 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        created_stations_sorted = sorted(
            created_stations,
            key=lambda x: (x.place_num is None, x.place_num),
        )
        response_data = [serialize_station(item) for item in created_stations_sorted]

        total_elapsed = time.time() - start_time
        logger.info(f"[POST] 모든 추천 프로세스 정상 종료 완료 (총 소요시간: {total_elapsed:.2f}초)")
        return Response(response_data, status=status.HTTP_200_OK)
