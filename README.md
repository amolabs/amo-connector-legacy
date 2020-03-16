# AMO Connector

## Pre
- 파일 하나는 하나의 Parcel으로 생각한다.
- Parcel Id는 `SHA256(filename | filehash)`로 정한다.

## Scenario
1. 데이터 서버에 파일이 추가된다.
1. Agent가 파일 생성을 감지한다.
1. Parcel ID와 파일을 AMO Blockchain에 Register Tx를 전송한다.
1. Agent2가 Request Tx를 AMO Explorer에서 확인한다.
1. 요청에 대해서 Grant Tx를 전송한다.
1. Grant한 사용자가 AMO storage에서 download한다.

## Components

### File system based AMO storage
- 기존의 download, upload 부분의 Ceph 어뎁터를 파일 시스템 기반 어뎁터로 변경
- Parcel Id <-> File path mapping
- SQLite3 -> Mariadb

#### Upload? Register?
```javascript
{
    "metadata": {
        "owner": user_identity,
        "name": "<FILE NAME>",
        "path": "<FILE PATH>"
    }
}
```

#### Filesystem metadata
| Index       | Data type     |
|:-----------:|:-------------:|
| owner       | char(40)      |
| parcel_name | varchar(512)  |
| parcel_path | varchar(1024) |
| created_at  | DateTime      |
| file_hash   | char(64)      |

`GET /api/v1/parcels/<parcel_id>`

### Data watcher
- File watcher 사용
- 감지되면 Parcel Id 생성 후 AMO storage에 upload(Parcel meta만 등록?)
### Request watcher
- 주기적으로 AMO Explorer에 Grant되지 않은 Request Tx 요청
- 감지되면 Grant Tx 전송

### TODO

- 대용량 파일 업로드/다운로드 처리
- 파일 저장 폴더 구조
- 파일 이름 규칙
- 파일 압축 전송 (e.g. GZIP, br, ...)
    - 다중 업로드/다운로드
- 추가된 메타데이터로 parcel 검색
- 제로 카피 고려
- ...
