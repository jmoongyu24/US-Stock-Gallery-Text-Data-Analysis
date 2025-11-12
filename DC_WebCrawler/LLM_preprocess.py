import openai # GPT-3.5 모델 사용
import pandas as pd # 로딩 및 전처리 수행
import os
import datetime # timestamp 데이터 변환
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import tiktoken # 토큰 계산용 (Optional)

# OpenAI API 키 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 프로젝트 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 데이터 파일 경로 설정
input_csv_path = os.path.join(BASE_DIR, "data", "contents.csv")
output_csv_path = os.path.join(BASE_DIR, "data", "classified_contents.csv")

# 데이터 불러오기
df = pd.read_csv("contents.csv")