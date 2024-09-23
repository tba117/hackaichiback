import random
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 認証済みユーザーのみ許可
def match_user(request):
    try:
        # ログイン中のユーザーを取得
        current_user = request.user

        # ログイン中のユーザーの趣味を取得
        current_user_hobbies = set(current_user.hobbys)

        if not current_user_hobbies:
            return Response({"error": "ログイン中のユーザーの趣味が設定されていません"}, status=status.HTTP_400_BAD_REQUEST)

        # すべてのユーザーを取得（ログイン中のユーザーを除外）
        other_users = User.objects.exclude(user_id=current_user.user_id)

        if not other_users.exists():
            return Response({"error": "他のユーザーが見つかりませんでした"}, status=status.HTTP_404_NOT_FOUND)

        # 趣味の共通数を計算して保存するリスト
        matching_users = []

        # 他のユーザーと共通の趣味を計算
        for user in other_users:
            user_hobbies = set(user.hobbys)
            common_hobbies_count = len(current_user_hobbies.intersection(user_hobbies))
            if common_hobbies_count > 0:
                matching_users.append((user, common_hobbies_count))

        # マッチングするユーザーがいない場合
        if not matching_users:
            return Response({"message": "共通の趣味を持つユーザーが見つかりませんでした"}, status=status.HTTP_404_NOT_FOUND)

        # 共通の趣味の数が多い順にソート
        matching_users.sort(key=lambda x: x[1], reverse=True)

        # 最大の共通数を持つユーザーを取得
        top_common_hobbies_count = matching_users[0][1]

        # 同じ共通数を持つユーザーをフィルタリング
        top_matching_users = [user for user, count in matching_users if count == top_common_hobbies_count]

        # 共通数がタイの場合、ランダムに1人選択
        matched_user = random.choice(top_matching_users)

        # マッチングしたユーザーの情報を返す
        matched_user_info = {
            "user_id": matched_user.user_id,
            "username": matched_user.username,
            "self_introduction": matched_user.self_introduction,
            "department": matched_user.department,
            "skils": matched_user.skils,
            "hobbys": matched_user.hobbys,
            "user_manual": matched_user.user_manual,
            "snsid": matched_user.snsid,
        }

        return Response({"matched_user": matched_user_info}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
