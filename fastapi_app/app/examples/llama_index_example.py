from llama_index import (
    VectorStoreIndex,
    ServiceContext,
    Document,
    StorageContext,
    load_index_from_storage,
)
from llama_index.vector_stores import ChromaVectorStore
from llama_index.llms import OpenAI
import chromadb
import os


class MenuVectorDB:
    def __init__(self, persist_dir="./chroma_db"):
        """
        초기화 함수
        Args:
            persist_dir (str): ChromaDB 저장 경로
        """
        self.persist_dir = persist_dir
        self.chroma_client = chromadb.PersistentClient(path=persist_dir)
        self.collection_name = "menu_collection"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name
        )

        # OpenAI 설정
        os.environ["OPENAI_API_KEY"] = "your-api-key-here"
        self.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
        self.service_context = ServiceContext.from_defaults(llm=self.llm)

    def create_or_load_index(self):
        """
        저장된 인덱스를 불러오거나 새로 생성
        """
        vector_store = ChromaVectorStore(chroma_collection=self.collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        if os.path.exists(self.persist_dir):
            # 기존 인덱스 불러오기
            index = load_index_from_storage(
                storage_context=storage_context, service_context=self.service_context
            )
        else:
            # 새 인덱스 생성
            index = VectorStoreIndex(
                [],
                storage_context=storage_context,
                service_context=self.service_context,
            )

        return index

    def add_menu_data(self, menu_data: str):
        """
        메뉴 데이터를 VectorDB에 추가
        Args:
            menu_data (str): 메뉴 정보 텍스트
        """
        document = Document(text=menu_data)
        index = self.create_or_load_index()
        index.insert(document)
        return index

    def query_menu(self, query_text: str, streaming: bool = False):
        """
        메뉴 정보 쿼리
        Args:
            query_text (str): 질문 텍스트
            streaming (bool): 스트리밍 응답 여부
        """
        index = self.create_or_load_index()
        query_engine = index.as_query_engine(streaming=streaming)

        if streaming:
            response = query_engine.query(query_text)
            for text in response.response_gen:
                print(text, end="", flush=True)
            print()
        else:
            response = query_engine.query(query_text)
            print("응답:", response)


def main():
    # VectorDB 인스턴스 생성
    menu_db = MenuVectorDB()

    # 샘플 메뉴 데이터
    sample_menu_data = """
    메뉴 정보:
    1. 김치찌개
    - 가격: 8,000원
    - 설명: 매콤하고 깊은 맛이 특징인 전통 한식
    - 인기도: 상

    2. 비빔밥
    - 가격: 9,000원
    - 설명: 신선한 야채와 고기가 어우러진 영양식
    - 인기도: 최상
    """

    # 메뉴 데이터 추가
    menu_db.add_menu_data(sample_menu_data)

    # 일반 쿼리 테스트
    print("\n일반 쿼리 테스트:")
    menu_db.query_menu("메뉴의 가격이 얼마인가요?")

    # 스트리밍 쿼리 테스트
    print("\n스트리밍 쿼리 테스트:")
    menu_db.query_menu("가장 인기있는 메뉴는 무엇인가요?", streaming=True)


if __name__ == "__main__":
    main()
