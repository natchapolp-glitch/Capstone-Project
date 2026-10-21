*** Settings ***
Documentation     Real Chrome UI flow on the presentation PC. Synthetic edits and automated confirmation are transport tests, not human ground truth.
Library           SeleniumLibrary    timeout=30s
Library           Collections
Library           DemoEvidence.py
Suite Setup       Start Demo Browser
Suite Teardown    Close All Browsers
Test Teardown     Capture Page Screenshot

*** Variables ***
${URL}            http://127.0.0.1:8090/demo
${PHOTO}          R74946CAAC57E
${TEST_ACTOR}     robot_framework_automated_test_not_human_ground_truth
${EXISTING_RECEIPT}    ${EMPTY}

*** Test Cases ***
01 Thai Page Loads And Confirmation Requires A Selected Run
    Wait Until Element Is Visible    id:ha-refresh
    Wait Until Element Contains    id:message    กดอ่านภาพด้วยระบบ
    Verify Thai Labels And Page
    ${photos}=    Get List Items    id:doc    values=True
    Length Should Be    ${photos}    59
    Click Button    id:confirm
    Element Should Contain    id:message    อ่านภาพหรือเลือกรายการที่บันทึกไว้ก่อน

02 Process Real Image And Display Detection OCR And JSON
    Select From List By Value    id:doc    ${PHOTO}
    List Selection Should Be    id:rotation    หมุนทวนเข็ม 90°
    Input Text    id:reviewer    ${TEST_ACTOR}
    Click Button    id:process
    Wait Until Element Contains    id:status    pending_review    timeout=180s
    Wait Until Element Is Enabled    id:process    timeout=180s
    Remember Current Run
    ${photo_src}=    Get Element Attribute    id:photo    src
    Should Contain    ${photo_src}    /api/detection-image?id=
    Wait For Condition    return document.getElementById('photo').complete && document.getElementById('photo').naturalWidth > 0
    Click Element    xpath://summary[contains(.,'ผลจากเครื่องมือก่อนผู้ใช้แก้ไข')]
    ${ocr}=    Get Text    id:ocr-output
    Should Not Be Empty    ${ocr}
    ${json}=    Get Text    id:json-output
    Should Contain    ${json}    items
    Element Should Contain    id:run-meta    tesseract
    Verify Thai Labels And Page

03 Missing Reviewer Is Rejected And Edits Reach MQTT And HA
    Clear Element Text    id:reviewer
    Click Button    id:confirm
    Wait Until Element Contains    id:message    Reviewer name is required
    Input Text    id:reviewer    ${TEST_ACTOR}
    Input Text    id:merchant    ROBOT FRAMEWORK TRANSPORT TEST - NOT HUMAN TRUTH
    Input Text    id:date    2026-10-21
    Input Text    id:total    45
    Input Text    id:currency    THB
    ${rows}=    Get Element Count    css:#items tr
    FOR    ${i}    IN RANGE    ${rows}
        Click Button    css:#items tr:first-child button
    END
    Click Button    id:add
    Input Text    css:#items input[data-key="name"]    AUTOMATED UI TEST ITEM
    Input Text    css:#items input[data-key="quantity"]    1
    Input Text    css:#items input[data-key="unit"]    item
    Input Text    css:#items input[data-key="unit_price"]    45
    Input Text    css:#items input[data-key="line_total"]    45
    Click Button    id:confirm
    Wait Until Element Contains    id:status    published    timeout=60s
    Click Button    id:ha-refresh
    Wait Until Element Contains    id:ha-output    ได้รับรายการที่เลือกแล้ว    timeout=30s
    ${event}=    Verify Stored Edit And HA
    Set Suite Variable    ${EVENT}    ${event}
    Element Should Contain    id:ha-output    ${EVENT}

04 Duplicate Confirmation Does Not Create Another Event
    Click Button    id:confirm
    Wait Until Element Contains    id:message    ${EVENT}
    Wait Until Element Is Enabled    id:process
    ${event}=    Verify Stored Edit And HA
    Should Be Equal    ${event}    ${EVENT}

05 Home Assistant Login And States Show The Received Event
    Go To    http://127.0.0.1:8123/config/tools/state
    Sign In To Home Assistant Privately
    Wait Until Keyword Succeeds    45s    1s    Home Assistant State Page Should Load
    Filter Home Assistant Demo Sensors
    Wait Until Keyword Succeeds    30s    1s    Home Assistant Should Display Test Event

*** Keywords ***
Start Demo Browser
    Check Preconditions
    IF    $EXISTING_RECEIPT
        Use Existing Test Run    ${EXISTING_RECEIPT}
    END
    ${options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    modules=selenium.webdriver
    Call Method    ${options}    add_argument    --headless\=new
    Call Method    ${options}    add_argument    --window-size\=1600,1000
    Open Browser    ${URL}    chrome    options=${options}
