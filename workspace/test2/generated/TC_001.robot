*** Settings ***
Library    RequestsLibrary
Library    JSONLibrary
Suite Setup    Create Session    api    http://mockoon.ariyanaragroup.com

*** Test Cases ***

TC_001
    ${resp}=    GET On Session    api    /api/v1/public/home
    Should Be Equal As Integers    ${resp.status_code}    200
