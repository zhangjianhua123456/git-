window.addEventListener('load',function(){
    var arrow_l=document.querySelector('.arrow_l');
    var arrow_r=document.querySelector('.arrow_r');
    var focus = document.querySelector('.focus');
    // 鼠标经过focus就显示按钮
    focus.addEventListener('mouseenter',function(){
        arrow_l.style.display='block';
        arrow_r.style.display='block';
        clearInterval(timer);
        timer=null;//清除定时器变量
    });
    focus.addEventListener('mouseleave',function(){
        arrow_l.style.display='none';
        arrow_r.style.display='none';
        timer = setInterval(function(){
            //手动调用点击时间
            arrow_r.click();
    
        },2000)
    });
    // 动态生成小圆圈
    var ul = focus.querySelector('ul');
    var ol = document.querySelector('.circle');
    var focusWidth = focus.offsetWidth;
    for(let i= 0 ; i<ul.children.length;i++){
        //创建小li
        let li= document.createElement('li');
        // 记录当前小圆圈的索引号 通过自定义属性
        li.setAttribute('index',i);
        ol.appendChild(li);
        // 小圆圈的排他思想
        li.addEventListener('click',function(){
            for(let i = 0; i<ol.children.length;i++){
                ol.children[i].className='';
                this.className='current';
                //当我们点击了某个小li 就拿到当前小li的索引号
                let index = this.getAttribute('index');
                num=index;
                circle=index;
                console.log(index);
                animate(ul,-index*focusWidth);
            }
        });
    }
    ol.children[0].className='current';
    var first = ul.children[0].cloneNode(true);
    ul.appendChild(first);
    //控制小圆圈的变化
    var circle =0;
    var num=0;
    var flag = true;
    arrow_r.addEventListener('click',function(){
       if(flag){
           flag = false;//节流阀
            // 如果走到了最后复制的一张图片,此时 我们的ul要快速复原 left=0
        if(num==ul.children.length-1){
            ul.style.left=0;
            num=0;
        }
        num++;
        animate(ul,-num*focusWidth,function(){
            flag=true;
        });
        circle++;
        if(circle==ul.children.length-1){
            circle=0;
        }
        // 调用函数
        circleChange();
       }
    });
    // 左侧按钮
    arrow_l.addEventListener('click',function(){
        if(flag){
            flag=false;
            // 如果走到了最后复制的一张图片,此时 我们的ul要快速复原 left=0
        if(num==0){
            num=ul.children.length-1;
            ul.style.left=-num*focusWidth+'px';  
        }
        num--;
        animate(ul,-num*focusWidth,function(){
            flag=true;
        });
        circle--;
        // 如果circle<0 说明第一张图片,则小圆圈要改为第4个小圆圈(3)
        if(circle<0){
            circle=ol.children.length-1;
        }
        // 调用函数
        circleChange();
        }
    });

    // 封装函数  
    function circleChange(){
        // 先清除其余小圆圈的current类名
        for(let i = 0; i<ol.children.length;i++){
            ol.children[i].className='';
        }
        // 留下当前小圆圈的current类名
        ol.children[circle].className='current';
    }
    // 10 自动播放轮播图
    var timer =setInterval(function(){
        //手动调用点击时间
        arrow_r.click();

    },2000)
})