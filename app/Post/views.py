from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from .serializers import PostSerializer
from ..models import Post

User = get_user_model()

# 投稿する
class PostCreateView(APIView):
    # ユーザー認証
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # ログインユーザーを投稿者として保存
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# 投稿を取得
class PostListView(APIView):
    # 認証必要なし
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        # すべての投稿を取得
        posts = Post.objects.all().order_by('-created_at')

        # シリアライズ
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# 投稿を削除
class PostDeleteView(APIView):
    # 投稿の削除は認証されたユーザーのみ
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id, *args, **kwargs):
        try:
            # 削除対象の投稿を取得
            post = Post.objects.get(id=post_id)

            # 投稿者のみが削除可能(pk:プライマリーキー)
            if post.user.pk != request.user.pk:
                print('投稿者:', post.user)
                print('削除者:', request.user)
                return Response({'error': 'この投稿を削除する権限がありません'}, status=status.HTTP_403_FORBIDDEN)
            
            # 投稿を削除
            post.delete()
            return Response({'message': '投稿を削除しました'}, status=status.HTTP_200_OK)
        
        except Post.DoesNotExist:
            return Response({'error': '投稿が見つかりません'}, status=status.HTTP_404_NOT_FOUND)