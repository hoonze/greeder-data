from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pathlib import Path

import pandas as pd
from konlpy.tag import Kkma
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np

import time
# Create your views here.

@api_view(['POST'])
def extraction(request):
    if request.method == 'POST':
        article = request.data['writing']

        extraction = Keyword_extraction()

        keywords = extraction.extract_from_article(article)
        return Response(keywords)


class Keyword_extraction():
    def __init__(self):
        self.kkma = Kkma()

    def extract_from_article(self, article):
        df_stopwords = pd.read_excel(
            Path.joinpath(Path.cwd(), "keywords", "files", 'stop_words.xlsx'), engine='openpyxl')

        stopwords = df_stopwords['형태'].tolist()
        # # 글을 문장별로 구분
        sentences = self.get_sentences(article)
        # 문장별 명사 추출
        nouns = self.get_nouns(sentences, stopwords)
        # 문장별 키워드 추출
        keywords = self.get_keywords(nouns, 5)

        return keywords

    def tf_idf(self, sentences):
        # 문장을 넣으면 문장 단위로 tf-idf 수치를 벡터화
        vectorizer = TfidfVectorizer()
        tfidf_mat = vectorizer.fit_transform(sentences).toarray()

        graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)

        # 정수 인덱스 이름 불러오기
        # print(vectorizer.get_feature_names())

        return graph_sentence

    def cv(self, sentences):
        # 텍스트를 토큰 매트릭스로 변환
        #  token_pattern = r"(?u)\b\w+\b" 1개의 단어도 포함되도록
        cv = CountVectorizer(token_pattern=r"(?u)\b\w+\b")
        cv_mat = normalize(cv.fit_transform(
            sentences).toarray().astype(float), axis=0)

        vocab = cv.vocabulary_
        idx_to_word = {vocab[word]: word for word in vocab}
        graph_word = np.dot(cv_mat.T, cv_mat)

        return idx_to_word, graph_word

    # 키워드 추출 메서드(num = 추출할 갯수)
    def get_keywords(self, nouns, num):
        idx_to_word, graph_word = self.cv(nouns)
        ranks = self.get_ranks(graph_word)
        sort_ranks = sorted(ranks, key=lambda k: ranks[k], reverse=True)

        keywords = []
        index = []
        for idx in sort_ranks[:num]:
            index.append(idx)
        for idx in index:
            keywords.append(idx_to_word[idx])

        return keywords

    # Text Rank 알고리즘
    def get_ranks(self, graph, d=0.85):  # d = damping factor
        A = graph
        matrix_size = A.shape[0]
        for id in range(matrix_size):
            A[id, id] = 0
            col_sum = np.sum(A[:, id])  # A[:, id] = A[:][id]
            if col_sum != 0:
                A[:, id] /= col_sum
            A[:, id] *= -d
            A[id, id] = 1

        B = (1-d) * np.ones((matrix_size, 1))

        ranks = np.linalg.solve(A, B)  # 연립방적식 Ax = b
        return {idx: r[0] for idx, r in enumerate(ranks)}

    # 문장별 구분 메서드
    def get_sentences(self, text):
        sentences = self.kkma.sentences(text)
        return sentences

    # 명사 추출 메서드
    def get_nouns(self, sentences, stopwords):
        nouns = []

        for sentence in sentences:
            if sentence is not '':
                # 품사정보 포함된 형태소 반환
                pos = self.kkma.pos(sentence)

                noun = []
                for word in pos:
                    # 일반 명사, 고유명사이고 불용어가 아닐 때 추가
                    if (word[1] == 'NNG' or word[1] == 'NNP') and word[0] not in stopwords:
                        noun.append(word[0])

                if len(noun) > 0:
                    nouns.append(' '.join(noun))
        return nouns
