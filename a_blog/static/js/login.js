function login_click(){
    let login_button = document.getElementById('login-button')
    login_button.addEventListener('click',function button_click(event){
        email = document.getElementById('email').value
        password = document.getElementById('password').value
        remember = document.getElementById('checkDefault').checked
        console.log(email,password,remember)

        // 加上csrf_token验证
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
        $.ajax({
            url:'login',
            method:'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data:{
                email: email,
                password: password,
                remember: remember
            },
            success:function(result){
                console.log('成功了吗')
                if(result['code']==400){
                    alert(result['message'])
                }else{
                    // alert(result['message'])
                    window.location.href = 'index'
                }
            },
            error: function(err) {
                console.log('请求失败', err)
                alert('网络或服务器异常')
            }
        })
    })
}


login_click()