// 定义 验证码点击函数
function captcha_click(){
    // 获取按钮元素
    let captcha_button = document.getElementById('button-addon2')
    // 绑定事件
    captcha_button.addEventListener('click',function send_captcha(event){
        // 获取邮箱输入框的值
        let email=document.getElementById('email').value
        // 检查邮箱是否为空
        if(!email){
            alert('请输入正确的邮箱')
            return;
        }

        // 发送ajax请求(jquery写法)
        $.ajax('captcha?email='+email,{
            method:'GET',
            success:function(result){
                if(result['code']==200){
                    // 成功发送

                    // 禁用按钮点击事件
                    console.log('按钮监控被警用')
                    captcha_button.removeEventListener('click',send_captcha)

                    // 倒计时
                    console.log('开始倒计时')
                    let count = 60 // 设置倒计时初始时间,单位为秒

                    //          setInterval每隔毫秒执行一次代码
                    let timer = setInterval(function(){
                        if(count<=0){
                            captcha_button.textContent='发送验证码'  // 恢复按钮文本
                            clearInterval(timer) // 清除定时器
                            captcha_click() // 重新回到绑定事件
                        }else{
                            // 更新按钮文本
                            captcha_button.textContent=count+'s'
                            count--  // 倒计时
                        }
                    },1000)

                    alert('验证码已发送，请注意查收')
                }else{
                    // console.log(result['message'])
                    // 发送失败，并返回错误信息
                    alert(result['message'])
                }
            },
            fail:function(error){
                console.log(error)
            }
        })

        
    })
}

// 定义 注册点击函数
function register_click(){
    // 获取按钮元素
    let register_button = document.getElementById('register-button')
    // 绑定监听事件
    register_button.addEventListener('click',function(envent){
        // console.log('监听到了点击按钮')
        username = document.getElementById('username').value
        email = document.getElementById('email').value
        captcha = document.getElementById('captcha').value
        password = document.getElementById('password').value
        console.log(username,email,captcha,password)
        // 加上csrf_token验证
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
        $.ajax({
            url:'register',
            method:'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data:{
                username: username,
                email: email,
                captcha: captcha,
                password: password
            },
            success:function(result){
                // console.log('成功接收信息')
                // console.log(result)
                if(result['code']==400){
                    alert(result['message'])
                }else{
                    // alert(result['message'])
                    window.location.href = 'login'
                }
            },
            fail:function(error){
                console.log(error)
            }
        })
    })
}



captcha_click()
register_click()