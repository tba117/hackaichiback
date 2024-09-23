import openai
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
import os

User = get_user_model()

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv('OPENAI_API_KEY')

@api_view(['GET'])
def generate_questions(request, user_id):
    try:
        print(openai.api_key)
        # ユーザーIDでユーザーを検索
        user = User.objects.get(user_id=user_id)

        # ユーザーの user_manual と hobbys を取得
        user_manual = user.user_manual
        hobbies = user.hobbys

        # user_manual がある場合は、それを使って質問を生成
        if user_manual:
            prompt = f"{user_id}さんのユーザーマニュアルを基に深堀する質問を5つ生成してください。質問ごとの\nは一つにしてください。マニュアルの内容: {user_manual}"
        # user_manual がない場合は、hobbys を基に質問を生成
        elif hobbies:
            prompt = f"{user_id}さんを深堀する質問を{hobbies}を参考に5つ生成してください。質問ごとの\nは1つにしてください。"
        else:
            # どちらもない場合はエラーメッセージを返す
            return Response({"error": "趣味もユーザーマニュアルも見つかりませんでした"}, status=status.HTTP_400_BAD_REQUEST)

        # OpenAI API呼び出し
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは有能な心理マスターです。"},
                {"role": "user", "content": prompt}
            ]
        )

        print(response.choices[0].message.content)
        # 質問を生成してリスト化
        generated_text = response.choices[0].message.content.strip()
        questions = generated_text.split('\n')

        return Response({"questions": questions}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'ユーザーが見つかりません'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def generate_profile(request, user_id):
    try:
        # ユーザーIDでユーザーを検索
        user = User.objects.get(user_id=user_id)
        user_id = user.user_id

        # クライアントから送信された解答を取得
        answers = request.data.get('answers',[])

        # 解答が存在しない場合はエラーレスポンス
        if not answers:
            return Response({"error": "解答が提供されていません"}, status=status.HTTP_400_BAD_REQUEST)
        
         # GPT-4に送信するプロンプトの作成
        prompt = f"以下の解答を元に、{user_id}さんのプロフィールを生成してください。\n\n"
        for i, answer in enumerate(answers, 1):
            prompt += f"質問{i}: {answer}\n"

        # OpenAI API呼び出し
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたはプロのプロフィール作成者です。"},
                {"role": "user", "content": prompt}
            ]
        )

        # GPT-4から生成されたプロフィールを抽出
        generated_profile = response.choices[0].message.content.strip()

        # 生成されたプロフィールをユーザーのuser_manualに保存
        user.user_manual = generated_profile
        user.save()

        return Response({"profile": generated_profile}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)