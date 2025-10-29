*** Settings ***
Library    RequestsLibrary
Library    JSONLibrary
Library    Collections
Suite Setup    Create Session    api    http://mockoon.ariyanaragroup.com

*** Test Cases ***

TC_001
    Log    ========== REQUEST ==========    console=yes
    Log    Method: GET    console=yes
    Log    Endpoint: /api/v1/public/home    console=yes
    ${resp}=    GET On Session    api    /api/v1/public/home
    Log    ========== RESPONSE ==========    console=yes
    Log    Status Code: ${resp.status_code}    console=yes
    Log    Response Headers: ${resp.headers}    console=yes
    Log    Response Body: ${resp.text}    console=yes
    Should Be Equal As Integers    ${resp.status_code}    200
