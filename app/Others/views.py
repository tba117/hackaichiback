import openai
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
import os
from celery import shared_task
from celery.result import AsyncResult

User = get_user_model()

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv('OPENAI_API_KEY')

# 質問を生成
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
    

# 回答から取説生成
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
    

# 感想からプロフィールを生成
@api_view(['POST'])
def update_profile_with_feedback(request, user_id):
    try:
        # ユーザーIDでユーザーを検索
        user = User.objects.get(user_id=user_id)

        # クライアントから送信された感想を取得
        feedback = request.data.get('feedback', "")

        # 感想がない場合はエラーレスポンス
        if not feedback:
            return Response({"error": "感想が提供されていません"}, status=status.HTTP_400_BAD_REQUEST)

        # 現在のプロフィールと感想を取得
        current_profile = user.user_manual if user.user_manual else "まだプロフィールが生成されていません。"

        # GPT-4に送信するプロンプトの作成
        prompt = (
            f"以下は現在の{user.username}さんのプロフィールです:\n\n{current_profile}\n\n"
            f"これに基づいて、以下の感想をもとに新しいプロフィールを生成してください。\n"
            f"感想: {feedback}"
        )

        # OpenAI API呼び出し
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたはプロのプロフィール作成者です。"},
                {"role": "user", "content": prompt}
            ]
        )

        # GPT-4から生成された新しいプロフィールを抽出
        updated_profile = response.choices[0].message.content.strip()

        # 新しいプロフィールをユーザーのuser_manualに保存
        user.user_manual = updated_profile
        user.save()

        return Response({"updated_profile": updated_profile}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'ユーザーが見つかりません'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# アドバイス生成
# タスクを呼び出す
# アドバイス生成と保存
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_advice_save(request, user_id):
    print("アドバイス生成開始")
    try:
        # マッチングしたユーザーを取得
        user = User.objects.get(user_id=user_id)
        print('user: ', user)
        
        # 必要な情報を取得
        profile = user.user_manual  # 生成されたプロフィール
        print(profile)
        hobbies = ', '.join(user.hobbys) if user.hobbys else "趣味は設定されていません"
        print(hobbies)
        skills = ', '.join(user.skils) if user.skils else "スキルは設定されていません"
        print(skills)

        # GPT-4に送信するプロンプトの作成
        prompt = f"""
        あなたの相手は {user.username} さんです。
        以下の情報を元に、この人と話すときのコツやアドバイスを生成してください：

        1. プロフィール: {profile}
        2. 趣味: {hobbies}
        3. スキル: {skills}

        この情報に基づいて、この人と親しみやすく、興味を持たれるような話し方や話題のアドバイスを3つお願いします。
        アドバイスごとの\nは一つにしてください。番号付きでアドバイスのみ生成してください。
        アドバイスは簡潔でいいので、一行程度で生成してください
        """

        print(prompt)

        # OpenAI API呼び出し
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは有能なカウンセラーです。"},
                {"role": "user", "content": prompt}
            ],
        )

        print('chatgpt:', response)

        # GPT-4から生成されたアドバイスを抽出
        advice = response.choices[0].message.content.strip()

        # アドバイスをユーザーのフィールドに保存
        user.advice = advice
        user.save()

        return Response({"message": "アドバイスが保存されました"}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "ユーザーが見つかりません"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 保存されたアドバイスを取得
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_advice(request, user_id):
    try:
        # マッチングしたユーザーを取得
        user = User.objects.get(user_id=user_id)

        # アドバイスが存在するか確認
        if user.advice:
            return Response({"advice": user.advice}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "アドバイスがまだ生成されていません"}, status=status.HTTP_404_NOT_FOUND)

    except User.DoesNotExist:
        return Response({"error": "ユーザーが見つかりません"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
