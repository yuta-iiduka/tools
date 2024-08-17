console.log("request json is called.")
class RequestJSON extends ObjectManager{
  static{
    this.csrf_token = document.querySelector("meta[name=csrf_token]").getAttribute("value");

  }
  constructor(url_get="/",url_post="/",func,error_func){
    super();
    this.group = "request";
    this.func = func;
    this.error_func = error_func;
    this.xhr = new XMLHttpRequest();
    this.url_get = url_get;
    this.url_post = url_post;
    this.res_data = {}; //レスポンスとして返却されたデータ
    this.init();
  }
  
  init(){
    let self = this;
		this.xhr.onload = function(){
			let READYSTATE_COMPLETED = 4;
			let HTTP_STATUS_OK = 200;
			if( this.readyState == READYSTATE_COMPLETED && this.status == HTTP_STATUS_OK ){
        self.res_data = JSON.parse(this.responseText);
				if(typeof(self.func) === "function"){
          self.func(self.res_data);
        }
      }else if( this.readyState == READYSTATE_COMPLETED && this.status != HTTP_STATUS_OK ){
        // 200ステータス以外の500ステータスだった場合
        if(typeof(self.error_func) === "function"){
          self.error_func(self.res_data);
        }
			}else{
        alert("通信に失敗しました。")
      }
		}
		return this;
  }

  set_func(func){
    this.func = func;
    return this;
  }

  set_error_func(func){
    this.error_func = func;
    return this;
  }

  set_url_get(url){
    this.url_get = url;
    return this;
  }

  set_url_post(url){
    this.url_post = url;
    return this;
  }

  post(data){
    if(data === undefined){data = {}}
    this.xhr.open("POST",this.url_post);
		this.xhr.setRequestHeader('Content-Type', 'application/json');
		this.xhr.setRequestHeader('X-CSRFToken', RequestJSON.csrf_token);
		this.xhr.send(JSON.stringify(data));
  }

  get(data){
    if(data === undefined){data = {}}
    this.xhr.open("GET",this.url_get);
		this.xhr.setRequestHeader('Content-Type', 'application/json');
		this.xhr.setRequestHeader('X-CSRFToken', RequestJSON.csrf_token);
		this.xhr.send(JSON.stringify(data));
  }

}