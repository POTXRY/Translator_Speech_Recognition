/* 첨부 파일 처리 핸들러
    - 참고문서
        1. https://purecho.tistory.com/68
        2. https://codepen.io/green526/embed/qBjZLex?height=537&default-tab=html%2Cresult&slug-hash=qBjZLex&editable=true&user=green526&ke-size=size16&name=cp_embed_1
*/


var FILE_NUM = 0; // 첨부된 파일 개수
var FILE_ARRAY = new Array(); // 첨부 파일 저장용 배열

// 파일 추가 함수

function addfile(obj){
    let max_file_count = 10;
    let attach_file_count = $('.filebox').length;
    let remain_file_count = max_file_count - attach_file_count;
    let current_file_count = obj.files.length; // 현재 첨부된 파일 개수
    $('#attached-file-list').attr('hidden', false)
    // 첨부파일 개수 확인

    if (current_file_count > remain_file_count){
        alert('첨부파일은 최대 ${max_file_count}개 까지 첨부 가능합니다. ')
    } else {
        for (const file of obj.files){
            // 파일이 음성 파일인지 검증
            if (validation(file)){
                // 파일을 배열에 담기
                let reader = new FileReader();
                reader.readAsDataURL(file); // 파일 읽기
                reader.onload = function (){
                    FILE_ARRAY.push(file); // 읽기 성공 -> 배열에 저장
                };
                // 파일 목록을 화면에 추가
                const img_path = `
                    <img src='/static/imgs/delete-doc.ico' width='20px' alt='문서삭제'>
                `;
                let html_data = `
                    <div class="filebox my-2 ml-2" id="file${FILE_NUM}">
                        <p class="name">
                            첨부파일 ${FILE_NUM + 1}: ${file.name}
                            <span>
                                <a class="delete" onclick="deleteFile(${FILE_NUM});"> ${img_path} </a>
                            </span>
                        </p>
                    </div>`;
                $('.file-list').append(html_data)
                FILE_NUM ++;
            } else {
                continue;
            }
        }
    }
    // 첨부 파일을 저장했으므로 form input 내용 삭제
    $('input[type=file]').val('');



}

// 파일을 form에 저장

function saveFilesToForm(){
    let form = $('form');
    let form_data = new FormData(form[0]);
    for(let i=0; i<FILE_ARRAY.length; i++ ){
        form_data.append('file', FILE_ARRAY[i])
    }
    return form_data;
}

// 첨부파일 검증

function validation(obj){
    // 파일 타입 검사
    // https://developer.mozilla.org/ko/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types 
    const fileTypes = [
        'audio/mpeg', // mp3
        'video/x-msvideo', //avi
        'audio/wav', // wav
    ];
     // 지원하지 않는 파일은 제외
     if (!fileTypes.includes(obj.type)){
        alert("지원하지 않는 파일 형식입니다. 첨부 불가 파일은 제외되었습니다.");
        return false;
    } else if (obj.name.length > 200){
        alert('파일명 길이가 200자 이상인 파일은 제외되었습니다.')
        return false;
    } else if (obj.size > (500 * 1024 * 1024)){
        alert('파일 크기가 500MB 초과한 파일은 제외되었습니다.')
        return false;
    } else if (obj.name.lastIndexOf('.') == -1){
        alert('확장자가 없는 파일은 제외되었습니다.')
        return false;
    }
    else {
        return true;
    }

}

// 첨부파일 삭제

function deleteFile(num){
    document.querySelector("#file" + num).remove();
    FILE_ARRAY.splice(num, 1)
    FILE_NUM--;
}





// 서버 전송 코드
$(function(){
    const result_text_area = $('result_text_area');
    result_text_area.attr('hidden', true)

    // '서버 전송하기' 버튼을 클릭한 경우 -> 서버 전송 처리
    let submit_btn = $('#submit_files');
    submit_btn.on('click', function(e){
        // 파일이 첨부되어 있는지 확인
        if (FILE_NUM===0){
            alert('첨부파일이 없습니다.\n 분석할 파일을 추가해 주세요.')
            return;
        }
        // 파일 첨부 영역 감추기, 업로드 스피너 시작
        $('#attach_area').attr('hidden', true);
        $('#p_bar_area_upload').attr('hidden', false);
        
        // 파일을 서버로 전송하기
        let form_data = saveFilesToForm();
        $.ajax({
            method: 'POST',
            url: `/File_Transcription/upload/files/Transcription`,
            data: form_data,
           
            // 이전 코드
            // dataType: false, // 서버로부터 받을 데이터 형식
            // contentType: 'json', // 받을 데이터 형식
            
            // 수정 코드
            dataType: 'json', // 서버로부터 받을 데이터 형식
            contentType: false, // 보내는 데이터 형식
            
            processData: false, 
            cache: false,
            success: function(result){
                console.log(result['status']);
                $('#p_bar_area_upload').attr('hidden', true);
                $('#p_bar_area_upload1').attr('hidden', true);
                $('#result_text_area').attr('hidden', false);
                process()
            },
            error: function(error){
                alert('에러 발생!!!, 다시시도 하세요.');
                console.log(error.status, error.statusText);
                return;
            } 
        });

    });

    // 화면 초기화 버튼을 클릭 했을 경우의 처리
    $('#clear-content-btn').on('click', function(e){
        location.reload(); // 새로고침
    })


    // 새로운 파일 처리를 클릭했을 경우의 처리
    $('#new-task-btn').on('click', function(e){
        location.reload(); // 새로고침
    })

});

function process(){
    $.ajax({
        method: 'POST',
        url: '/File_Transcription/process',
        data: JSON.stringify({}),
        dataType: 'json', // 서버로부터 받을 데이터 형식
        contentType: 'application/json', // 보내는 데이터 형식
        success: function(result){
            console.log(result);
            $('#p_par_area_process').attr('hidden', true);
            $('#textarea_label').remove();
            $('#floatingTextarea2').val(result['0']);
            $('#new-task-btn').attr('hidden', false);
        },
        error: function(error){
            alert('에러가 발생했습니다ㅠㅠ\n관리자에게 문의해 주세요.');
            console.log(error.status, error.statusText);
            location.href = '/File_Transcription';
        }
    });
}