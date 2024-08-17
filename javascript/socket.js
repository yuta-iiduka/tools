
// after : socket.io.js
/**
 * This is "WEBSocket Builder" class
 */
class WEBSB{
    static{
        this.cnt = 0;
        this.list = {};
        this.NAMES = {CONNECT:"connect",JOIN:"join",LEAVE:"leave",ROOM:"FROMROOM",SERVER:"FROMSERVER"};
        this.CALLBACKES = {CONNECT:"connect",JOIN:"join",LEAVE:"leave"};
    }

    constructor(user_id,room_id){
        this.id = WEBSB.cnt++;
        this.socket = io();
        this.room_id = room_id;
        this.user_id = user_id;

        this.from_room_event = null;
        this.from_server_event = null;

        this.init();

        WEBSB.list[this.id] = this;
    }

    init(){
        const self = this;
        // WEBSocketコネクション用
        this.socket.on(WEBSB.NAMES.CONNECT,function(data){
            self.socket.emit(WEBSB.CALLBACKES.CONNECT,self.dict("connect!"));
        });

        // ルーム参加用
        this.socket.on(WEBSB.NAMES.JOIN,function(data){
            console.log("join",data);
        });

        // ルーム退出用
        this.socket.on(WEBSB.NAMES.LEAVE,function(data){
            console.log("leave",data);
        });

        // 同一ルームからのブロードキャスト対応用
        this.socket.on(WEBSB.NAMES.ROOM,function(data){
            if(typeof(self.from_room_event)==="function"){
                self.from_room_event(data);
            }
        });

        // サーバからのブロードキャスト対応用
        this.socket.on(WEBSB.NAMES.SERVER,function(data){
            if(typeof(self.from_server_event)==="function"){
                self.from_server_event(data);
            }
        });

        return this;
    }

    dict(data={},to=""){
        const d = {};
        const room = to==="" ? this.room_id : to;
        if( typeof(data) === "string"){
            d = {data: {msg: data}, to: room}
        }else{
            d = {data: data, to: room}
        }
        return d;
    }

    join(room_id){
        const to = room_id === undefined ? this.room_id: room_id;
        this.socket.emit(WEBSB.CALLBACKES.JOIN,this.dict(`join ${this.user_id}`,to));
    }

    leave(room_id){
        const to = room_id === undefined ? this.room_id: room_id;
        this.socket.emit(WEBSB.CALLBACKES.LEAVE,this.dict(`leave ${this.user_id}`,to));
    }

    send(callback_name,room_id,data){
        const to = room_id === undefined ? this.room_id: room_id;
        this.socket.emit(callback_name,this.dict(data,to));
    }

    add_listener(name,callback=function(data){console.log(data)}){
        WEBSB.NAMES[name] = name;
        this.socket.on(name,function(data){
            if(typeof(callback)==="function"){
                callback(data);
            }
        });

        return this;
    }



}