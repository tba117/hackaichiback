from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import User

class UserMatchingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        # マッチング元のユーザー情報を取得
        user1 = User.objects.filter(user_id=user_id).first()

        if not user1:
            return Response({'message': 'ユーザーが見つかりません'}, status=404)
        
        # ユーザー1いがにのすべてのユーザーを取得
        other_users = User.objects.exclude(user_id=user_id)

        max_common_hobbys_count = 0
        matched_user = None

        # ユーザー1の趣味リストを取得
        user1_hobbys = set(user1.hobbys)
        
        for user in other_users:
            # ほかのユーザーの趣味リスト
            user_hobbys = set(user.hobbys)

            # 共通の趣味の数を計算
            common_hobbys_count = len(user1_hobbys & user_hobbys) # 共通する趣味の数

            # 最大共通数が見つかった場合、ユーザーを更新
            if common_hobbys_count > max_common_hobbys_count:
                max_common_hobbys_count = common_hobbys_count
                matched_user = user

        if matched_user:
            response_data = {
                "message": f"ユーザー{user1.user_id}のマッチング相手は{matched_user.user_id}です",
                "matched_user": {
                    "user_id": matched_user.user_id,
                    "username": matched_user.username,
                    "self_introduction": matched_user.self_introduction,
                    "department": matched_user.department,
                    "skil": matched_user.skil,
                    "hobbys": matched_user.hobbys,
                    "user_manual": matched_user.user_manual,     
                    "snsid": user.snsid, 
                    "common_hobbys_count": max_common_hobbys_count,
                    "common_hobbys": list(user1_hobbys & set(matched_user.hobbys))
                }
            }
            return Response(response_data, status=200)
        else:
            return Response({"message": "マッチングするユーザーが見つかりませんでした"}, status=404)