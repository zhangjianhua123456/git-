function animate(obj, target,callback) {
    
    clearInterval(obj.timer);
    obj.timer = setInterval(function () {
        // 把步长值改为整数  不要出现小数
        var step = (target - obj.offsetLeft) / 5;
        step = step > 0 ? Math.ceil(step) : Math.floor(step);
        if (obj.offsetLeft == target) {
            clearInterval(obj.timer);
            //回调函数写到定时器结束里面
            if(callback){
                callback();
                console.log(callback);
            }
            
        }
        obj.style.left = obj.offsetLeft + step + 'px';
    }, 30)
};