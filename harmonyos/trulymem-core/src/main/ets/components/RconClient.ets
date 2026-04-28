import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';
import {RConResult,parseRCONBuffer,buildPacket,GetAuth} from '../components/tools';

type RConCallback = (result: RConResult) => void;

export class RConClient
{
   public isActive: boolean; //是否可用标志位，随tcp状态更改
   private tcp: socket.TCPSocket; //socket连接
   private ipAddress: socket.NetAddress; //ip地址
   private passWord: string; //密码
   private isConnecting: boolean = false; // 标记连接是否正在进行中，防止并发连接
   private closeHandler: (() => void) | null = null; // 保存 close 事件处理器引用以便清理
   private authResolve: (() => void) | null = null; // 认证完成信号
   private nextPacketId: number = 1; // 递增的包序号，避免重复

   constructor(ip:string,LPort:number,PassWord:string) {
     this.isActive = false;
     this.tcp = socket.constructTCPSocketInstance();
     this.ipAddress = {
       address: ip,
       port: LPort
     }
     this.passWord = PassWord;//初始化tcp连接相关配置
   }
  //连接服务器
   async setConnect(timeOut:number,callBack:RConCallback)//异步获取服务器连接
   {
     if (this.isConnecting) {
       // Already connecting, return an error via callback
       callBack(RConResult.error("ALREADY_CONNECTING", "A connection attempt is already in progress"));
       return;
     }
     this.isConnecting = true;
     let finished = false; // To ensure we set isConnecting to false only once
     const setFinished = () => {
       if (!finished) {
         finished = true;
         this.isConnecting = false;
       }
     };

     // 清理旧的事件监听器
     this.cleanupListeners();

     let connectOptions: socket.TCPConnectOptions = {
       address: this.ipAddress,
       timeout: timeOut
     };

     await this.tcp.connect(connectOptions).then(() => {
       console.info('Connection established');
       let result:RConResult = RConResult.result(undefined,"tcp_ok")
       // 注册 close 事件并保存引用
       this.closeHandler = () => {
         this.isActive = false;
       };
       this.tcp.on('close', this.closeHandler);
       //发送认证信息
       GetAuth(this.tcp,this.passWord,3,(result:RConResult)=>{
         setFinished();
         if(!result.success) {
           callBack(result);
           // 通知等待的 sendAfterAuth 认证失败
           this.notifyAuthComplete();
         }
         else
         {
           this.isActive = true;
           callBack(result);
           // 通知等待的 sendAfterAuth 认证成功
           this.notifyAuthComplete();
         }

       })
     }).catch((err: BusinessError) => {
       setFinished();
       let result = RConResult.error(JSON.stringify({ code: err.code, message: err.message }), "tcp_fail");
       callBack(result);
       this.notifyAuthComplete();
     });
   }

   /**
    * 通知认证流程完成（供 sendAfterAuth 等待机制使用）
    */
   private notifyAuthComplete(): void {
     if (this.authResolve) {
       this.authResolve();
       this.authResolve = null;
     }
   }

   /**
    * 获取下一个递增包序号（跳过 -1，因为 -1 在 RCON 协议中表示认证失败）
    */
   private getNextPacketId(): number {
     const id = this.nextPacketId;
     this.nextPacketId++;
     if (this.nextPacketId === -1 || this.nextPacketId > 2147483646) {
       this.nextPacketId = 1;
     }
     return id;
   }

   /**
    * 清理所有事件监听器
    */
   private cleanupListeners(): void {
     this.tcp.off("close");
     this.tcp.off("message");
     this.closeHandler = null;
   }

   async sendMessage(message:string,type:number,callBack:RConCallback)
   {//发送一条指令
     if(!this.isActive)//错误重连机制
     {
       await this.setConnect(1000,(result:RConResult)=>{
         if (!result.success) {
           // Connection failed, call the outer callback with the error
           callBack(result);
           return;
         }
         // 重连后需要重新认证，不能直接发送命令
         // 等待认证完成后再发送消息
         this.sendAfterAuth(message, type, callBack);
       })
     }
     else {
       this.sendWithResponse(message, type, callBack);
     }
   }

   /**
    * 发送消息并等待响应（正常路径）
    */
    private sendWithResponse(message: string, type: number, callBack: RConCallback): void {
      const packetId = this.getNextPacketId();
      const messageHandler = (info: socket.SocketMessageInfo) => {
        const buffer: ArrayBuffer = info.message;
        const result = parseRCONBuffer(buffer);
        callBack(result);
        this.tcp.off("message", messageHandler);
      };
      this.tcp.on("message", messageHandler);

      let sendOption: socket.TCPSendOptions = { data: buildPacket(packetId, type, message) };
     this.tcp.send(sendOption).catch((err: BusinessError) => {
       let result = RConResult.error(JSON.stringify({ code: err.code, message: err.message }), "send_auth_fail");
       callBack(result);
       this.tcp.off("message", messageHandler);
       this.setDisconnect();
     });
   }

   /**
    * 重连后等待认证完成再发送消息
    * 使用 Promise 等待机制替代轮询
    */
   private sendAfterAuth(message: string, type: number, callBack: RConCallback): void {
     // 创建认证等待 Promise（最多 5 秒）
     const authPromise = new Promise<boolean>((resolve) => {
       this.authResolve = () => resolve(this.isActive);
       // 超时兜底
       setTimeout(() => {
         if (this.authResolve) {
           this.authResolve = null;
           resolve(false);
         }
       }, 5000);
     });

     authPromise.then((authSuccess: boolean) => {
       if (authSuccess) {
         this.sendWithResponse(message, type, callBack);
       } else {
         let result = RConResult.error("AUTH_TIMEOUT", "Authentication timed out after reconnect");
         callBack(result);
       }
     });
   }

  async resetServer(ip:string,password:string,port:number,timeout:number,callback:RConCallback)
  {//重新设置服务器配置
    this.ipAddress = {
      address:ip,
      port:port
    }
    this.passWord = password;
    this.setDisconnect();//断开放弃使用的tcp连接
    await this.setConnect(timeout,callback);
  }
  setDisconnect()
  {
    // 清理所有事件监听器
    this.cleanupListeners();
    // 断链
    try {
      this.tcp.close();
    } catch {
      // Socket already closed
    }
    this.isActive = false;
  }

}
