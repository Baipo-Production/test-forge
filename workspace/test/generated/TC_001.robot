*** Settings ***
Library    RequestsLibrary
Library    JSONLibrary
Suite Setup    Create Session    api    http://localhost

*** Test Cases ***

TC_001
    No Operation
    No Operation
    No Operation
    No Operation
    ${resp}=    GET On Session    api    http://mockoon.ariyanaragroup.com/api/v1/public/home    params=${query}    headers=${headers}    data=${payload}
    Should Be Equal As Integers    ${resp.status_code}    200
