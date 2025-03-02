import os
import re
import json
from prettytable import PrettyTable

staff_file = 'staff.json'
pending_staff_file = 'pending_staff_file.json'
fire_staff_file = 'fire_staff_file.json'
to_do_list = 'to_do_list.json'
notice_file = 'notice_file.json' # 공지사항
team_communication = 'team_commnuication.json' # 팀 쳇
admin_inquiry = 'admin_inquiry.json' # 관리자에게 1:1 문의

def valid(prompt, valid = None, is_int = False):
    while True:
        user_choice = input(prompt).strip()

        if not user_choice:
            print('오류: 공백이 입력되었습니다.')
            print()

            continue

        if valid and user_choice not in valid:
            print(f'오류: {valid} 외에 다른 것은 입력될 수 없습니다.')
            print()

            continue

        if is_int:
            if not user_choice.isdigit():
                print('오류: 숫자만 입력할 수 있습니다.')
                print()

                continue

            return int(user_choice) # int형으로 반환

        return user_choice # str형으로 반환

def found_file(file, header = None):
    if not os.path.exists(file):
        with open(file, 'w', newline='') as file_:
            json.dump([], file_, ensure_ascii=False, indent=2)

found_file(staff_file, ['user_name', 'password', 'name', 'phone_number', 'role'])
found_file(pending_staff_file, ['user_name', 'password', 'name', 'phone_number', 'role'])
found_file(fire_staff_file, ['user_name', 'password', 'name', 'phone_number', 'role'])
found_file(to_do_list, ['할 일 목록 추가', '완료한 업무 체크', '업무 진행 상황 확인', '할 일 삭제'])
found_file(notice_file, ['공지사항', '내용'])
found_file(team_communication, ['팀원에게 공지', '내용'])
found_file(admin_inquiry, ['관리자에게 공지', '내용'])

def add_default_admin():
    try:
        with open(staff_file, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                data = []

    except(FileNotFoundError, json.JSONDecodeError):
            data = []

    default_admin = {
        'id' : 'admin_id',
        'pw' : 'admin_pw_123',
        'name' : '관리자1',
        'phone' : '010-0000-0000',
        'role' : '관리자'
    }

    if not any(admin.get('role') == '관리자' for admin in data):
        data.append(default_admin)

        with open(staff_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)

class User_Manager:
    def registser(self, user_id, password, user_name, phone):
        with open(staff_file, 'r', newline='', encoding='utf-8') as f_:
            exist_data = json.load(f_)

            if not isinstance(exist_data, list):
                exist_data = [exist_data]

        with open(pending_staff_file, 'r', newline='', encoding='utf-8') as f_:
            try:
                pending_data = json.load(f_)

                if not isinstance(pending_data, list):
                    pending_data = [pending_data]
            except (FileNotFoundError, json.JSONDecodeError):
                pending_data = []

        # any 말고 set으로도 가능함
        # exist_ids = {user.get(id) for user in exist_data}
        # pending_ids = {user.get(id) for user in pending_data}
        # if user_id in exist_ids or user_id in pending_ids

        if any(user.get('id') == user_id for user in exist_data) or any(user.get('id') == user_id for user in pending_data):
            print(f'❌ {user_id}은(는) 직원이거나 승인 대기중인 아이디입니다.')
            print()

            return None

        new_user = {
            'id' : user_id,
            'pw' : password,
            'name' : user_name,
            'phone' : phone,
            'role' : '승인 대기중'
        }

        pending_data.append(new_user)

        with open(pending_staff_file, 'w', newline='', encoding='utf-8') as f_:
            json.dump(pending_data, f_, ensure_ascii=False, indent=2)

        print(f'✅ {user_id} 직원 계정이 가입 신청되었습니다. (승인 대기중)')
        print('✅ 관리자가 승인하여야 로그인할 수 있습니다.')
        print()

    def login(self, user_id, password):
        attempts = 0

        while attempts < 5:
            try:
                with open(staff_file, 'r', encoding='utf-8') as f_:
                    data = json.load(f_)

                    if not isinstance(data, list):
                        print('❌ 데이터 형식이 잘못되었습니다.')
                        print()

                with open(pending_staff_file, 'r', encoding='utf-8') as pending_staff_data:
                    pending_data = json.load(pending_staff_data)

                    if not isinstance(pending_data, list):
                        print('❌ 데이터 형식이 잘못되었습니다.')
                        print()

            except FileNotFoundError:
                print('❌ 사용자 데이터 파일이 존재하지 않습니다.')
                print()

                data = []
                pending_data = []
            except json.JSONDecodeError:
                print('❌ JSON 파일 형식이 잘못되었습니다.')
                print()

                data = []
                pending_data = []

            pending_data_center = {user.get('id') for user in pending_data}

            if user_id in pending_data_center:
                print(f'❌ {user_id}는 현재 승인 대기중입니다.')

                return None

            for user in data:
                if user.get('id') == user_id and user.get('pw') == password:
                    print(f'✅ 로그인 성공! {user_id} (권한: {user.get('role', 'N/A')})')
                    print()

                    return user.get('role'), user

            attempts += 1
            print(f'❌ 로그인 실패! ({attempts}/5) 아이디 또는 비밀번호를 다시 입력해주세요.')
            print()

            if attempts < 5:
                user_id = valid('👤 직원 ID 다시 입력해주세요: ').strip()
                password = valid('🔑 비밀번호를 다시 입력해주세요: ').strip()

        print('🚨 5회 연속 로그인 실패! 프로그램을 종료합니다.')
        exit()

def phone_number_modifying(user_id, password, user_name, phone_number):
    user_manager = User_Manager()

    phone_number = phone_number.replace('-','')

    if len(phone_number) == 11:
        phone = f'{phone_number[:3]}-{phone_number[3:7]}-{phone_number[7:]}'

    user_manager.registser(user_id, password, user_name, phone)

class Admin_Member_Manager:
    def staff_list(self):
        pretty = PrettyTable()

        print('📋 직원 목록:')
        pretty.field_names = ['번호', 'ID', 'PW', '이름', '전화번호', '권한']

        try:
            with open(staff_file, 'r', encoding='utf-8') as staff_files:
                staff_data = json.load(staff_files)

                if isinstance(staff_data, dict):
                    staff_data = [staff_data]

                for i, staff_info in enumerate(staff_data, start=1):
                    pretty.add_row([
                        i,
                        staff_info.get('id', 'N/A'),
                        staff_info.get('pw', 'N/A'),
                        staff_info.get('name', 'N/A'),
                        staff_info.get('phone', 'N/A'),
                        staff_info.get('role', 'N/A'),
                    ])

        except (FileNotFoundError, json.JSONDecodeError):
            print('❌ 직원 데이터가 존재하지 않습니다.')
            print()

        print(pretty)

    def pending_staff_add(self):
        pretty = PrettyTable()

        print('📋 직원 목록:')
        pretty.field_names = ['번호', 'ID', 'PW', '이름', '전화번호', '권한']

        try:
            with open(pending_staff_file, 'r', encoding='utf-8') as pending_files:
                pending_data = json.load(pending_files)

                if isinstance(pending_data, dict):
                    pending_data = [pending_data]

                for i, pending_staff_info in enumerate(pending_data, start=1):
                    pretty.add_row([
                        i,
                        pending_staff_info.get('id', 'N/A'),
                        pending_staff_info.get('pw', 'N/A'),
                        pending_staff_info.get('name', 'N/A'),
                        pending_staff_info.get('phone', 'N/A'),
                        pending_staff_info.get('role', 'N/A'),
                    ])
        except (FileNotFoundError, json.JSONDecodeError):
            print('❌ 직원 데이터가 존재하지 않습니다.')
            print()

        print(pretty)
        print()

        try:
            pending_staff_number = valid('승인할 직원 번호: ', is_int=True) - 1
            pending_choice = valid('승인(y/n): ', ['Y', 'y', 'N', 'n'])

            if pending_choice.lower() == 'y':
                if 0 <= pending_staff_number < len(pending_data):
                    approved_user = pending_data.pop(pending_staff_number)
                    approved_user['role'] = '직원'

                    try:
                        with open(staff_file, 'r', encoding='utf-8') as staff_files:
                            staff_data = json.load(staff_files)

                            if not isinstance(staff_data, list):
                                staff_data = [staff_data]

                    except (FileNotFoundError, json.JSONDecodeError):
                        staff_data = []

                    staff_data.append(approved_user)
                    #pending_data.pop(pending_staff_number) 활성화시 전체삭제

                    with open(staff_file, 'w', encoding='utf-8') as staff_files:
                        json.dump(staff_data, staff_files, ensure_ascii=False, indent=2)

                    with open(pending_staff_file, 'w', encoding='utf-8') as pending_files:
                        json.dump(pending_data, pending_files, ensure_ascii=False, indent=2)

                    print(f'✅ {approved_user['id']} 직원이 승인되었습니다!')
                    print()

                else:
                    print('❌ 잘못된 직원 번호입니다.')
                    print()
            else:
                print('❌ 직원 승인을 취소하셨습니다.')
                print()


        except ValueError:
            print('❌ 숫자를 입력해주세요.')
            print()


    def remove_staff(self):
        pretty = PrettyTable()

        print('📋 직원 목록:')
        pretty.field_names = ['번호', 'ID', 'PW', '이름', '전화번호', '권한']

        try:
            with open('staff.json', 'r', encoding='utf-8') as staff_files:
                staff_datas = json.load(staff_files)

                if isinstance(staff_datas, dict):
                    staff_datas = [staff_datas]

                for i, staff_list_info in enumerate(staff_datas, start=1):
                    pretty.add_row([
                        i,
                        staff_list_info.get('id', 'N/A'),
                        staff_list_info.get('pw', 'N/A'),
                        staff_list_info.get('name', 'N/A'),
                        staff_list_info.get('phone', 'N/A'),
                        staff_list_info.get('role', 'N/A')
                    ])

        except (FileNotFoundError, json.JSONDecodeError):
            staff_datas = []

        print(pretty)
        print()

        try:
            remove_staff_number = valid('해고시킬 직원 번호를 입력: ', is_int=True) - 1
        except ValueError:
            print('❌ 숫자를 입력해주세요')
            print()

        if 0 <= remove_staff_number >= len(staff_datas):
            print('❌ 잘못된 직원 번호입니다.')
            print()

        check_fire = valid('정말 해고하시겠습니까? (y/n): ', ['y', 'Y', 'n', 'N'])

        if check_fire.lower() == 'y':
            fired_staff = staff_datas.pop(remove_staff_number)
            fired_staff['role'] = '해고'

            try:
                with open('fire_staff_file', 'r', encoding='utf-8') as fire_staff_files:
                    fire_staff_datas = json.load(fire_staff_files)

                    if isinstance(fire_staff_datas, dict):
                        fire_staff_datas = [fire_staff_datas]

            except (FileNotFoundError, json.JSONDecodeError):
                fire_staff_datas = []

            fire_staff_datas.append(fired_staff)

            with open(fire_staff_file, 'w', encoding='utf-8') as fire_staff_files:
                json.dump(fire_staff_datas, fire_staff_files, ensure_ascii=False, indent=2)

            with open(staff_file, 'w', encoding='utf-8') as staff_files:
                json.dump(staff_datas, staff_files, ensure_ascii=False, indent=2)

            print(f'✅ {fired_staff['id']}는 정상적으로 해고되었습니다.')
            print()

        else:
            print('❌ 해고가 취소되었습니다.')
            print()

    def reinstatement(self):
        pretty = PrettyTable()

        print('📋 직원 목록:')
        pretty.field_names = ['번호', 'ID', 'PW', '이름', '전화번호', '권한']

        try:
            with open('fire_staff_file.json', 'r', encoding='utf-8') as fire_staff_files:
                fire_staff_datas = json.load(fire_staff_files)

                if isinstance(fire_staff_datas, dict):
                    fire_staff_datas = [fire_staff_datas]

                for i, fire_staff_info in enumerate(fire_staff_datas, start=1):
                    pretty.add_row([
                        i,
                        fire_staff_info.get('id', 'N/A'),
                        fire_staff_info.get('pw', 'N/A'),
                        fire_staff_info.get('name', 'N/A'),
                        fire_staff_info.get('phone', 'N/A'),
                        fire_staff_info.get('role', 'N/A')
                    ])

        except (FileNotFoundError, json.JSONDecodeError):
            fire_staff_datas = []

        print(pretty)
        print()

        try:
            fire_staff_number = valid('복직시킬 직원 번호: ', is_int=True) - 1

        except ValueError:
            print('❌ 숫자를 입력해주세요')
            print()

        if 0 <= fire_staff_number < len(fire_staff_datas):
            check_reinstatement = valid('정말 복직시키겠습니까? (y/n): ', ['y', 'Y', 'n', 'N'])

            if check_reinstatement.lower() == 'y':
                reinstatement_staff = fire_staff_datas.pop(fire_staff_number)
                reinstatement_staff['role'] = '직원'

                try:
                    with open('staff.json', 'r', encoding='utf-8') as staff_files:
                        staff_datas = json.load(staff_files)

                        if isinstance(staff_datas, dict):
                            staff_datas = [staff_datas]

                except (FileNotFoundError, json.JSONDecodeError):
                    staff_datas = []

                staff_datas.append(reinstatement_staff)

                with open('fire_staff_file.json', 'w', encoding='utf-8') as fire_staff_files:
                    json.dump(fire_staff_datas, fire_staff_files, ensure_ascii=False, indent=2)

                with open('staff.json', 'w', encoding='utf-8') as staff_files:
                    json.dump(staff_datas, staff_files, ensure_ascii=False, indent=2)

                print(f'✅ {reinstatement_staff['id']} 직원을 복직시켰습니다.')
                print()

            else:
                print('❌ 복직을 취소시켰습니다.')
                print()

        else:
            print('❌ 잘못된 직원 번호입니다.')
            print()


    def promotion_staff(self):
        pretty = PrettyTable()

        print('📋 직원 목록:')
        pretty.field_names = ['번호', 'ID', 'PW', '이름', '전화번호', '권한']

        try:
            with open('staff.json', 'r', encoding='utf-8') as staff_files:
                staff_datas = json.load(staff_files)

                if isinstance(staff_datas, dict):
                    staff_datas = [staff_datas]

                for i, staff_info in enumerate(staff_datas, start=1):
                    pretty.add_row([
                        i,
                        staff_info.get('id', 'N/A'),
                        staff_info.get('pw', 'N/A'),
                        staff_info.get('name', 'N/A'),
                        staff_info.get('phone', 'N/A'),
                        staff_info.get('role', 'N/A')
                    ])

        except (FileNotFoundError, json.JSONDecodeError):
            staff_datas = []

        print(pretty)
        print()

        try:
            promotion_staff_number = valid('승진시킬 직원 번호를 입력하세요: ', is_int=True) - 1
        except ValueError:
            print('❌ 숫자만 입력해주세요')
            print()

        if 0 <= promotion_staff_number < len(staff_datas):
            check_promotion = valid('승진시키겠습니까? (y/n): ', ['y', 'Y', 'n', 'N'])

            if check_promotion.lower() == 'y':
                promotion_staff = staff_datas[promotion_staff_number]
                promotion_staff['role'] = '관리자'

                with open('staff.json', 'w', encoding='utf-8') as staff_files:
                    json.dump(staff_datas, staff_files, ensure_ascii=False, indent=2)

                    print(f'✅ {promotion_staff['id']}을 승진시켰습니다.')
                    print()
            else:
                print('❌ 승진을 취소하였습니다.')
                print()

        else:
            print('❌ 잘못된 직원 번호입니다.')
            print()

    def demotion_staff(self):
        pretty = PrettyTable()

        print('📋 직원 목록:')
        pretty.field_names = ['번호', 'ID', 'PW', '이름', '전화번호', '권한']

        try:
            with open('staff.json', 'r', encoding='utf-8') as staff_files:
                staff_datas = json.load(staff_files)

                if isinstance(staff_datas, dict):
                    staff_datas = [staff_datas]

                for i, staff_info in enumerate(staff_datas, start=1):
                    pretty.add_row([
                        i,
                        staff_info.get('id', 'N/A'),
                        staff_info.get('pw', 'N/A'),
                        staff_info.get('name', 'N/A'),
                        staff_info.get('phone', 'N/A'),
                        staff_info.get('role', 'N/A')
                    ])

        except (FileNotFoundError, json.JSONDecodeError):
            staff_datas = []

        print(pretty)
        print()

        try:
            demotion_staff_number = valid('강등시킬 직원 번호를 입력하세요: ', is_int=True) - 1
        except ValueError:
            print('❌ 숫자만 입력해주세요')
            print()

        if 0 <= demotion_staff_number < len(staff_datas):
            check_demotion = valid('강등시키겠습니까? (y/n): ', ['y', 'Y', 'n', 'N'])

            if check_demotion.lower() == 'y':
                demotion_staff = staff_datas[demotion_staff_number]
                demotion_staff['role'] = '직원'

                with open('staff.json', 'w', encoding='utf-8') as staff_files:
                    json.dump(staff_datas, staff_files, ensure_ascii=False, indent=2)

                    print(f'✅ {demotion_staff['id']}을 강등시켰습니다.')
                    print()
            else:
                print('❌ 강등을 취소하였습니다.')
                print()

        else:
            print('❌ 잘못된 직원 번호입니다.')
            print()

class Staff_Member_Manager:
    def info_inquiry(self, user_id):
        # 비밀번호 변경, 전화번호 수정
        pretty = PrettyTable()

        print('📋 내 정보 보기')
        pretty.field_names = ['ID', 'PW', '이름', '전화번호', '권한']

        try:
            with open('staff.json', 'r', encoding='utf-8') as staff_files:
                staff_datas = json.load(staff_files)

                if isinstance(staff_datas, dict):
                    staff_datas = [staff_datas]

                for staff_info in staff_datas:
                    if staff_info.get('id') == user_id:
                        pretty.add_row([
                            staff_info.get('id', 'N/A'),
                            staff_info.get('pw', 'N/A'),
                            staff_info.get('name', 'N/A'),
                            staff_info.get('phone', 'N/A'),
                            staff_info.get('role', 'N/A'),
                        ])

        except (FileNotFoundError, json.JSONDecodeError):
            staff_datas = []

        print(pretty)
        print()

        print('🏢 [정보 수정]')
        print('1. 비밀번호 변경')
        print('2. 전화번호 변경')

        int_user_choice = valid('👉 입력: ', ['1', '2'], is_int=True)

        if int_user_choice == 1:
            change_password = valid('👉 변경할 비밀번호 입력: ')
            check_change_password = valid('✅ 정말 변경하시겠습니까? (y/n): ', ['y', 'Y', 'n', 'N'])

            if check_change_password.lower() == 'y':
                updated = False

                for staff_info in staff_datas:
                    if staff_info.get('id') == user_id:
                        staff_info['pw'] = change_password
                        updated = True
                        break

                if updated:
                    try:
                        with open('staff.json', 'w', encoding='utf-8') as staff_files:
                            json.dump(staff_datas, staff_files, ensure_ascii=False, indent=2)

                        print(f'✅ {change_password} 로 비밀번호가 변경되었습니다.')
                        print()

                    except Exception as e:
                        print(f'❌ 파일 저장 중 오류 발생 : {e}')
                        print()

                else:
                    print('❌ 해당 ID를 가진 직원이 존재하지 않습니다.')
                    print()

        if int_user_choice == 2:
            change_phone = valid('👉 변경할 전화번호 입력: ')
            check_change_phone = valid('👉 정말 변경하시겠습니까? (y/n): ', ['y', 'Y', 'n', 'N'])

            change_phone = change_phone.replace('-', '')

            if len(change_phone) == 11:
                new_phone = f'{change_phone[:3]}-{change_phone[3:7]}-{change_phone[7:]}'

            if check_change_phone.lower() == 'y':
                updated = False

                for staff_info in staff_datas:
                    if staff_info.get('id') == user_id:
                        staff_info['phone'] = new_phone
                        updated = True
                        break

                if updated:
                    try:
                        with open('staff.json', 'w', encoding='utf-8') as staff_files:
                            json.dump(staff_datas, staff_files, ensure_ascii=False, indent=2)

                        print(f'✅ 전화번호를 {change_phone} 로 변경하였습니다.')
                        print()

                    except Exception as e:
                        print(f'❌ 파일 저장 중 오류 발생 : {e}')
                        print()

                else:
                    print('❌ 해당 ID를 가진 직원이 존재하지 않습니다.')
                    print()

    def sfaff_work(self):
        # 오늘 할 일 추가, 완료한 업무 체크, 업무 진행 상황 확인, 할 일 삭제 -> json
        try:
            with open('to_do_list.json', 'r', encoding='utf-8') as to_do_lists:
                to_do_datas = json.load(to_do_lists)

                if isinstance(to_do_datas, dict):
                    to_do_datas = [to_do_datas]

        except (FileNotFoundError, json.JSONDecodeError):
            to_do_datas = []

        print('🏢 [업무 보고 및 할 일 관리]')
        print('1. 오늘 할 일 목록')
        print('2. 오늘 할 일 추가')
        print('3. 완료한 업무 체크')
        print('❌4. 업무 진행 상황 확인')
        print('5. 할 일 삭제')

        int_staff_choice = valid('👉 입력: ', ['1', '2', '3', '4', '5'], is_int=True)

        if int_staff_choice == 1:
            if not to_do_datas:
                default_to_do_lists = [
                    {'번호': 1, "내용": '메일 확인 및 회신 📧', '완료': False},
                    {'번호': 2, "내용": '회의 일정 확인 및 준비 📅', '완료': True},
                    {'번호': 3, "내용": '문서 작성 및 정리 📄', '완료': False},
                    {'번호': 4, "내용": '자료 조사 및 보고서 작성 📑', '완료': True},
                    {'번호': 5, "내용": '업무 관련 소프트웨어 업데이트 및 관리 🖥️', '완료': False}
                ]

                if isinstance(to_do_datas, list):
                    to_do_datas.extend(default_to_do_lists)

                else:
                    to_do_datas = default_to_do_lists

                try:
                    with open('to_do_list.json', 'w', encoding='utf-8') as to_do_lists:
                        json.dump(to_do_datas, to_do_lists, ensure_ascii=False, indent=2)

                except Exception as error:
                    print(f'❌ 오류: 파일 저장 중 오류 발생 -> {error}')
                    print()

            print('📋 오늘 할 일 목록')
            for task in to_do_datas:
                T_F = '✅ 완료' if task['완료'] else '❌ 미완료'
                print(f'{task['번호']} - {task['내용']} / {T_F}')
            print()

        elif int_staff_choice == 2:
            try:
                with open('to_do_list.json', 'r', encoding='utf-8') as to_do_lists:
                    to_do_datas = json.load(to_do_lists)

                    if isinstance(to_do_datas, dict):
                        to_do_datas = [to_do_datas]

            except (FileNotFoundError, json.JSONDecodeError):
                to_do_datas = []

            to_do_add = valid('✅ 새롭게 추가할 할 일: ')
            check_to_do_add = valid('추가하시겠습니까? (y/n): ', ['y', 'Y', 'n', 'N'])

            if check_to_do_add.lower() == 'y':
                last_number = to_do_datas[-1]['번호'] + 1 if to_do_datas else 1
                new_task = {'번호': last_number, '내용': to_do_add, '완료': False}
                to_do_datas.append(new_task) # 번호 지정, 내용, 미완료는 디폴트 false로

                try:
                    with open('to_do_list.json', 'w', encoding='utf-8') as to_do_lists:
                        json.dump(to_do_datas, to_do_lists, ensure_ascii=False, indent=2)

                    print(f'✅ 내용: {to_do_add} 이 추가되었습니다.')
                    print()

                except Exception as error:
                    print(f'❌ 오류: 파일 저장 중 오류 발생 -> {error}')

        elif int_staff_choice == 3: # 완료한 업무 체크 -> 완료한 업무만 출력
            pretty = PrettyTable()

            print('📋 완료한 업무 체크:')
            pretty.field_names = ['번호', '내용', '완료']

            try:
                with open('to_do_list.json', 'r', encoding='utf-8') as to_do_lists:
                    to_do_datas = json.load(to_do_lists)

                    if isinstance(to_do_datas, dict):
                        to_do_datas = [to_do_datas]

            except (FileNotFoundError, json.JSONDecodeError):
                to_do_datas = []

            completed = [comp for comp in to_do_datas if comp['완료'] == True]

            if completed:
                for i, list_info in enumerate(completed, start=1):
                    status = '✅ 완료' if list_info.get('완료', False) else '❌ 미완료'

                    pretty.add_row([
                        i,
                        list_info.get('내용', 'N/A'),
                        status
                    ])

                print(pretty)
                print()

        #elif int_staff_choice == 4: # 업무 진행 상황 확인 어캐하라고

        elif int_staff_choice == 5: # 할 일 삭제
            pretty = PrettyTable()

            print('📋 완료한 업무 체크:')
            pretty.field_names = ['번호', '내용', '완료']
            
            try:
                with open('to_do_list.json', 'r', encoding='utf-8') as to_do_lists:
                    to_do_datas = json.load(to_do_lists)

                    if isinstance(to_do_datas, dict):
                        to_do_datas = [to_do_datas]

            except (FileNotFoundError, json.JSONDecodeError):
                to_do_datas = []
            
            for i, list_info in enumerate(to_do_datas, start=1):
                status = '✅ 완료' if list_info.get('완료', False) else '❌ 미완료'

                pretty.align['번호'] = 'c'
                pretty.align['내용'] = 'l'
                pretty.align['완료'] = 'c'
                pretty.max_width['내용'] = 37

                pretty.add_row([
                    i,
                    list_info.get('내용', 'N/A'),
                    status
                ])

            print(pretty)
            print()

            max_check = max([task['번호'] for task in to_do_datas], default=1) # todolist 파일에 있는 번호의 맥시멈 구하기

            try:
                remove_work = valid(
                    '✅ 삭제할 할 일 번호를 입력해주세요:  ',
                    [str(i) for i in range(1, max_check + 1)],
                    is_int = True
                ) # 미니멈 1, 맥시멈은 max_check로 구해진 값 으로 제한

            except ValueError as error:
                print(f'오류: 숫자만 입력할 수 있습니다. -> {error}')

            check_remove_work = valid('정말 삭제하시겠습니까? (y/n): ', ['y', 'Y', 'n', 'N'])

            if check_remove_work.lower() == 'y':
                # 예랴고 했을 경우 그 번호에 대한 딕셔너리 삭제 구현해야함
                to_do_datas.pop(remove_work - 1)

                try:
                    with open('to_do_list.json', 'w', encoding='utf-8') as to_do_lists:
                        json.dump(to_do_datas, to_do_lists, ensure_ascii=False, indent=2)

                except (FileNotFoundError, json.JSONDecodeError):
                    to_do_datas = []

                print(f'✅ {remove_work}번의 할 일을 삭제하였습니다.')
                print()

        else:
            print('1-5번을 제외한 숫자는 입력할 수 없습니다.')
            print()
        
    def communication_wiht_team_member(self, user):
        # 공지사항 확인, 팀채팅, 1:1문의 (관리자에게) -> 공지사항 json, 팀 채팅 json, 1:1문의 json
        # 삭제 기능 미구현 해도 됨, 한다면 팀채팅, 1:1문의에 올린 채팅 삭제 정도

        try:
            with open('notice_file.json', 'r', encoding='utf-8') as notices:
                notice_datas = json.load(notices)

                if isinstance(notice_datas, dict):
                    notice_datas = [notice_datas]

            with open('team_commnuication.json', 'r', encoding='utf-8') as team_communications:
                team_communication_datas = json.load(team_communications)

                if isinstance(team_communication_datas, dict):
                    team_communication_datas = [team_communication_datas]

            with open('admin_inquiry.json', 'r', encoding='utf-8') as admin_inquirys:
                admin_inquiry_datas = json.load(admin_inquirys)

                if isinstance(admin_inquiry_datas, dict):
                    admin_inquiry_datas = [admin_inquiry_datas]

            with open('staff.json', 'r', encoding='utf-8') as staff_files:
                staff_datas = json.load(staff_files)

                if isinstance(staff_datas, dict):
                    staff_datas = [staff_datas]

        except (FileNotFoundError, json.JSONDecodeError):
            notice_datas = []
            team_communication_datas = []
            admin_inquiry_datas = []
            staff_datas = []

        print('🏢 [팀원과의 커뮤니케이션]')
        print('1. 공지사항 확인')
        print('2. 팀 채팅')
        print('❌3. 1:1문의 (관리자에게)')
        print()

        # 공지사항 : 중요, 위급, 즉시확인, 경고, 보통, 안내, 공지, 업데이트, 참고, 알림, 유의
        # 내용 : ----
        # 중요! -> !는 추가적으로 만들어야함
        # 내용: ---- 나오게

        user_choice = valid('👉 입력: ', ['1', '2', '3'], is_int=True)

        if user_choice == 1:
            if not notice_datas:
                default_notice = [
                    {'공지사항': '알림',
                    '내용': """공지사항에는
                    🔴 긴급성 높은 공지:
                    - 중요
                    - 위급
                    - 즉시확인
                    - 경고
                    
                    🟡 일반적인 공지
                    - 보통
                    - 안내
                    - 공지
                    - 업데이트
                    
                    🟢 유용한 공지
                    - 참고
                    - 알림
                    - 유의"""
                     }
                ]

            notice_datas.extend(default_notice)

            try:
                with open('notice_file.json', 'w', encoding='utf-8') as notices:
                    json.dump(notice_datas, notices, ensure_ascii=False, indent=2)

                    if isinstance(notice_datas, dict):
                        notice_datas = [notice_datas]

            except (FileNotFoundError, json.JSONDecodeError):
                notice_datas = []

            pretty = PrettyTable()

            print('📋 공지사항:')
            pretty.field_names = ['번호', '공지사항', '내용']
            
            pretty.align['번호'] = 'c'
            pretty.align['공지사항'] = 'c'
            pretty.align['내용'] = 'l'

            for i, notice_info in enumerate(notice_datas, start=1):
                pretty.add_row([
                    str(i),
                    notice_info.get('공지사항', 'N/A'),
                    notice_info.get('내용', 'N/A').replace('\n                    ', '\n').strip()
                ])

            print(pretty)
            print() # 관리자만 추가 가능한걸로

        elif user_choice == 2:
            # 스탭 파일에서 로그인 되어있는 계정의 이름을 가져와야함
            # 프리티 필드는 [이름] [내용]으로만 하는걸로
            # 2번 들어와서 어떠한 키를 누르면 종료하게 되는걸로
            # 종료하기전에는 계속 채팅을 칠 수 있게 이거맞아?

            user_name = [name['name'] for name in staff_datas]

            if user['name'] not in user_name:
                print(f'❌ 로그인한 계정이 직원 파일에 존재하지 않습니다.')
                return

            #print('📋 [팀 채팅]')

            pretty = PrettyTable()
            pretty.field_names = ['이름', '내용']
            pretty.align['이름'] = 'l'
            pretty.align['내용'] = 'l'

            while True:
                content = valid('내용 입력: ').strip()
                exit_button = valid('종료를 원할 경우 (y/n): ', ['y', 'Y', 'n', 'N'])

                pretty.add_row([user['name'], content])

                print('📋 현재 채팅 기록')
                print(pretty)
                print()

                team_communication_datas.append({user['name']: content})
                # 딕셔너리 형태로 'you': 'uu' 이런식으로 저장되는 것 까지 구현 완료
                # 딕셔너리 형태 1개에 계속 추가가 되는지 확인 필요
                try:
                    with open('team_commnuication.json', 'w', encoding='utf-8') as team_communications:
                        json.dump(team_communication_datas, team_communications, ensure_ascii=False, indent=2)

                except (FileNotFoundError, json.JSONDecodeError):
                    team_communication_datas = []

                if exit_button.lower() == 'y':
                    print('✅ 팀 채팅 종료 ✅')
                    print()
                    break




def main_menu():
    user_manager = User_Manager()
    admin_member_manager = Admin_Member_Manager()
    staff_member_manager = Staff_Member_Manager()

    while True:
        print('🏢 [직원 관리 시스템]')
        print('1. 회원가입')
        print('2. 로그인')
        print('3. 종료')

        user_choice = valid('👉 입력: ', ['1', '2', '3'], is_int = True)

        if user_choice == 1:
            user_id = valid('👤 직원 ID: ')
            password = valid('🔑 비밀번호: ')
            user_name = valid('📛 이름: ')
            phone_number = valid('📞 휴대폰 번호: ')
            phone_number_modifying(user_id, password, user_name, phone_number)

        elif user_choice == 2:
            user_id = valid('👤 직원 ID: ')
            password = valid('🔑 비밀번호: ')
            role, user = user_manager.login(user_id, password)

            if role == '관리자':
                while True:
                    print('📌 [메뉴 - 관리자]')
                    print('1. 직원 목록 조회')
                    print('2. 대기중인 직원 승인')
                    print('3. 직원 삭제')
                    print('4. 직원 복직')
                    print('5. 직원 승진 (관리자로)')
                    print('6. 직원 강등 (직원으로)')
                    print('7. 로그아웃')
                    print()

                    admin_choice = valid('👉 선택: ', ['1', '2', '3', '4', '5', '6', '7'], is_int = True)

                    if admin_choice == 1:
                        admin_member_manager.staff_list()

                    elif admin_choice == 2:
                        admin_member_manager.pending_staff_add()

                    elif admin_choice == 3:
                        admin_member_manager.remove_staff()

                    elif admin_choice == 4:
                        admin_member_manager.reinstatement()

                    elif admin_choice == 5:
                        admin_member_manager.promotion_staff()

                    elif admin_choice == 6:
                        admin_member_manager.demotion_staff()

                    elif admin_choice == 7:
                        print('🚨 로그아웃 🚨')
                        print()
                        break

                    else:
                        print('1-7번을 제외한 숫자는 입력할 수 없습니다.')
                        print()

                        # 관리자 권한 부분은 9할 완성
                        # 관리자 권한 쪽 건드린다면 회원가입 아이디, 비번, 이름 부분 풀매치 땡기는거?
                        # 추가적으로 관리자가 관리자를 해임 못시키는 구조
                        # + 사장단 파일만들어서 사장단이 관리자를 해임시키는 구조
            elif role == '직원':
                while True:
                    print('📌 [메뉴 - 직원]')
                    print('1. 본인 정보 조회 및 수정') # 내정보보기(이름,전화번호,비밀번호), 비밀번호 변경, 전화번호 수정
                    print('❌2. 출퇴근 관리 시스템') # 출근 기록, 퇴근 기록, 근무시간 조회, 이번주 근무 시간 통계 -> 사실상 불가능
                    print('3. 업무 보고 및 할 일 관리') # 오늘 할 일 추가, 완료한 업무 체크, 업무 진행 상황 확인, 할 일 삭제 -> json
                    print('4. 팀원과의 커뮤니케이션') # 공지사항 확인, 팀채팅, 1:1문의 (관리자에게) -> 공지사항 json, 팀 채팅 json, 1:1문의 json
                    print('❌5. 급여 및 휴가 관리') # 급여 내역 조회, 연차 사용 내역 확인, 휴가 신청, 잔여 연차 조회
                    print('❌6. 교육 및 공지사항') # 사내 교육 자료, 회사 정책 확인, 최근 공지사항 -> 교육 자료 + 회사 정책 확인 json, 공지사항 json
                    print('7. 로그아웃')
                    print()
                    
                    int_staff_choice = valid('👉 선택: ', ['1', '2', '3', '4', '5', '6', '7'], is_int=True)

                    if int_staff_choice == 1:
                        staff_member_manager.info_inquiry(user_id)

                    elif int_staff_choice == 3:
                        staff_member_manager.sfaff_work()

                    elif int_staff_choice == 4:
                        staff_member_manager.communication_wiht_team_member(user)

                    elif int_staff_choice == 7:
                        print('🚨 프로그램 종료 🚨')
                        exit()

                    else:
                        print('1-7번을 제외한 숫자는 입력할 수 없습니다.')
                        print()

        elif user_choice == 3:
            print('🚨 프로그램 종료 🚨')
            exit()

        else:
            print('1-3번을 제외한 숫자는 입력할 수 없습니다.')
            print()

if __name__ == "__main__":
    add_default_admin()
    main_menu()

'''
staff_data = pending_data[number] 여기서 = 는 값을 바꿔라가 아닌
pending_data[number]를 참조하라는 뜻
깃 허브 테스트
깃 허브 테스트깃 허브 테스트깃 허브 테스트깃 허브 테스트깃 허브 테스트깃 허브 테스트깃 허브 테스트



'''
