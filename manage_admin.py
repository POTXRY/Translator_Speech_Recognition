from server.views.sql_database import db, User
from server.__init__ import create_app  # type: ignore # Flask 애플리케이션 가져오기

# Flask 애플리케이션 생성
app = create_app()  # create_app() 호출로 Flask 앱 객체 생성

def make_user_admin(email):
    """
    특정 사용자를 관리자로 지정합니다.
    :param email: 관리자로 지정할 사용자의 이메일 주소
    """
    with app.app_context():  # 애플리케이션 컨텍스트 활성화
        user = User.query.filter_by(email=email).first()  # 사용자 조회
        if user:
            if user.is_admin:
                print(f"{user.email} 님은 이미 관리자입니다.")
            else:
                user.is_admin = True
                db.session.commit()
                print(f"User {user.email} is now an admin.")
        else:
            print("User not found.")

if __name__ == "__main__":
    # 이메일 입력받아 관리자로 지정
    email = input("Enter the email of the user to make admin: ")
    make_user_admin(email)