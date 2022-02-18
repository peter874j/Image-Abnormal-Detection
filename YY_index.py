<meta charset="utf-8" xmlns="http://www.w3.org/1999/html" xmlns="http://www.w3.org/1999/html">
<html lang="en">


<html>

<style>
    .wrap {
        /* width: 100px; */
        text-align: left;
        line-height: 50px;
        float: left;
    }

    .command {
        background: pink;
        height: 300px;
        text-align: center;
        line-height: 50px;
        float: left;
    }

    .cam1 {
        background: pink;
        height: 300px;
        text-align: center;
        line-height: 50px;
        /* float: left; */
    }

    .temp {
        display: flex;
        align-content: center;
    }

    .cam2 {
        background: pink;
        height: 300px;
        text-align: center;
        line-height: 50px;
        float: right;
    }

    .motionResult-style {
        background-color: gray;
        height: 30%;
        width: 30%;
    }

    .start_and_end {
        color: blue;
        display: none;
    }
</style>

<script src="https://code.jquery.com/jquery-3.2.1.js"></script>
<script>
    function motion_result() {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/motion_result",
            success: function (result) {
                for (var i = 0; i < result['step_num'].length; i++) {
                    if (result['step_result'][i] == "NO") {
                        var stepConsole = document.getElementById(`Step_result${result['step_num'][i]}`);
                        stepConsole.style = "color:green;font-size:50px;"
                    }
                    if (result['step_result'][i] == "YES") {
                        var stepConsole = document.getElementById(`Step_result${result['step_num'][i]}`);
                        stepConsole.style = "color:red;font-size:50px;"
                    }

                    if (result['step_num'] == '0') {
                        var stepEnd = document.getElementById('end');
                        stepEnd.style.display = "none"
                    }
                    if (result['step_num'] == '1') {
                        var stepStart = document.getElementById('start');
                        stepStart.style.display = "block"
                    }
                    if (result['step_num'] == '4') {
                        for (var i = 1; i <= 4; i++) {
                            var stepConsole = document.getElementById(`Step_result${i}`);
                            stepConsole.style = "color:black;font-size:50px;"
                        }
                        var stepEnd = document.getElementById('end');
                        stepEnd.style.display = "block"
                        var stepStart = document.getElementById('start');
                        stepStart.style.display = "none"
                    }
                }
            },
            error: function (result) {
                swal("Error", { button: "OK!" });
            }
        })
    }


    // for motions
    window.setInterval(function () {
        var myImageElement = document.getElementById('cameraFeed');
        var timestamp = new Date().getTime()
        var newUrl = "{{ url_for('video_feed_0') }}" + '?_=' + timestamp;
        myImageElement.src = newUrl;
        motion_result()
    }, 150);

    // // for hands
    window.setInterval(function () {
        var myImageElement = document.getElementById('cameraHands');
        var timestamp = new Date().getTime()
        var newUrl = "{{ url_for('video_feed_1') }}" + '?_=' + timestamp;
        myImageElement.src = newUrl;
    }, 100);

    window.setInterval(function () { // load the data from your endpoint into the div
        $("#now_time").load("/now_time.txt")
    }, 1000)

</script>

<head>
    <title>Stream</title>
</head>

<body>

    <!-- 子頁面跳轉 -->
    <div class="wrap">
        <form action="/sec_page" method="get">
            <h5><input type="submit" value="Configure" style="font-size:30px" /></h5>
        </form>
        <h1>
            <div class="Header">AUO_VisionGuard</div>
        </h1>
    </div>

    <!--  右方主鏡頭 -->
    <div class="cam2">
        <h1>Video Stream 2</h1>
        <img id="cameraHands" src="{{ url_for('video_feed_1') }}">
    </div>

    <div class='temp'>
        <!-- 左方主鏡頭 -->
        <div class="cam1">
            <h1>Video Stream 1</h1>
            <img id="cameraFeed" src="{{ url_for('video_feed_0') }}">
        </div>

        <!-- 動作流程檢測結果 -->
        <div class='motionResult-style'>
            <h1>動作流程狀態</h1>
            <p id="start" style="font-size:50px;" class="start_and_end">Start</p>
            <p id="Step_result1" style="font-size:50px;">Step 1. Work_Rack to Jig</p>
            <p id="Step_result2" style="font-size:50px;">Step 2. Jig to Finish</p>
            <p id="Step_result3" style="font-size:50px;">Step 3. Placement to Jig</p>
            <p id="Step_result4" style="font-size:50px;">Step 4. Jig to Work_Rack</p>
            <p id="end" style="font-size:50px;" class="start_and_end">End</p>
        </div>
    </div>

    <!-- 時間顯示 -->
    <div id="now_time" style="position: absolute; right:900; top:900;
    font-size:62px;background-color:#FF4500;">
        <h1>{{ user_time }} </h1>
    </div>

</body>

</html>
