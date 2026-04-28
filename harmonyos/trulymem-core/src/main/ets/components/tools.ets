import { socket } from '@kit.NetworkKit';
import { BusinessError } from '@kit.BasicServicesKit';
import { util } from '@kit.ArkTS';

const MAXLENGTH:number = 1447;

/**
 * 手动 UTF-8 编码（替代已弃用的 util.TextEncoder.encode/encodeInto）
 */
function utf8Encode(str: string): Uint8Array {
  const bytes: number[] = [];
  for (let i = 0; i < str.length; i++) {
    const code = str.charCodeAt(i);
    if (code <= 0x7F) {
      bytes.push(code);
    } else if (code <= 0x07FF) {
      bytes.push(0xC0 | (code >> 6));
      bytes.push(0x80 | (code & 0x3F));
    } else if (code <= 0xFFFF) {
      bytes.push(0xE0 | (code >> 12));
      bytes.push(0x80 | ((code >> 6) & 0x3F));
      bytes.push(0x80 | (code & 0x3F));
    } else {
      bytes.push(0xF0 | (code >> 18));
      bytes.push(0x80 | ((code >> 12) & 0x3F));
      bytes.push(0x80 | ((code >> 6) & 0x3F));
      bytes.push(0x80 | (code & 0x3F));
    }
  }
  return new Uint8Array(bytes);
}

export class RConResult {
  success: boolean = false;  // 操作是否成功
  errorCode?: string;        // 错误码
  errorMessage?: string;     // 错误描述
  rawData?: ArrayBuffer;
  resultText ?:string;  // 附加数据
  type ?:number;
  id ?:number;
static result(data?:ArrayBuffer,stringResult?:string,type?:number,id?:number):RConResult{
    const result = new RConResult();
    result.success = true;
    if(data !== undefined){result.rawData = data;}
    if(stringResult !== undefined){result.resultText = stringResult;}
    if(type !== undefined){result.type = type;}
    if(id !== undefined){result.id = id;}
    return result;
}
  static error(code: string, message: string): RConResult {
    const result = new RConResult();
    result.success = false;
    result.errorCode = code;
    result.errorMessage = message;
    return result;
  }
}

export function  buildPacket(packetId: number, type: number, payload: string): ArrayBuffer
{
   // 使用自定义 UTF-8 编码器替代已弃用的 util.TextEncoder
   const encodedPayload: Uint8Array = utf8Encode(payload);
  const payloadWithTerminator: Uint8Array = new Uint8Array(encodedPayload.length + 1);
  payloadWithTerminator.set(encodedPayload);
  payloadWithTerminator[encodedPayload.length] = 0x00; // 添加空终止符

  // 检查编码后的字节长度是否符合 RCON 协议限制（payload + null terminator + padding <= 1460）
  // 即 encodedPayload.length + 1 (null) + 1 (padding) <= 1460 - 4 (length) - 4 (id) - 4 (type)
  // 即 encodedPayload.length <= 1446
  if (encodedPayload.length > MAXLENGTH) {
        console.warn(`[RCON] Payload truncated from ${encodedPayload.length} to ${MAXLENGTH} bytes (RCON protocol limit)`);
        // 截断到最大字节长度
        const truncated = new Uint8Array(MAXLENGTH);
        truncated.set(encodedPayload.subarray(0, MAXLENGTH));
        payloadWithTerminator.set(truncated);
  }

  // 计算各字段长度（单位：字节）
  const idFieldSize: number = 4;
  const typeFieldSize: number = 4;
  const payloadSize: number = payloadWithTerminator.byteLength;
  const paddingSize: number = 1;

  // 总长度计算（不包含长度字段自身）
  const packetLength: number =
    idFieldSize +
      typeFieldSize +
      payloadSize +
      paddingSize;

  // 创建二进制缓冲区
  const buffer: ArrayBuffer = new ArrayBuffer(
    packetLength + 4  // 包含长度字段自身
  );
  const view: DataView = new DataView(buffer);

  // 写入字段（小端序）
  view.setInt32(0, packetLength, true);   // 长度字段
  view.setInt32(4, packetId, true);       // ID字段
  view.setInt32(8, type, true);           // 类型字段

  // 写入负载内容
  const payloadStartOffset: number = 12;
  new Uint8Array(buffer, payloadStartOffset).set(payloadWithTerminator);

  // 添加填充字节
  const paddingOffset: number = payloadStartOffset + payloadSize;
  new Uint8Array(buffer, paddingOffset, paddingSize).fill(0x00);

  return buffer;
}

export function parseRCONBuffer(buffer: ArrayBuffer): RConResult
{
  const view: DataView = new DataView(buffer);

  // 基础头校验
  if (buffer.byteLength < 12) {
    return RConResult.error("INVALID_HEADER", "Packet length less than 12 bytes");
  }

  // 小端序解析头字段
  const length: number = view.getInt32(0, true);
  const requestId: number = view.getInt32(4, true);
  const type: number = view.getInt32(8, true);

  // 负载终止符定位
  let payloadEnd: number = 12;
  const maxPosition: number = Math.min(12 + length - 10, buffer.byteLength);
  while (payloadEnd < maxPosition) {
    if (view.getUint8(payloadEnd) === 0x00) break;
    payloadEnd++;
  }

  // 提取有效负载
  const payloadBytes: Uint8Array = new Uint8Array(
    buffer.slice(12, payloadEnd)
  );
  // 解码 UTF-8 字符串
  const textDecoderOptions: util.TextDecoderOptions = {
    fatal: false,
    ignoreBOM: true
  };
  const decodeToStringOptions: util.DecodeToStringOptions = {
    stream: false
  };
  const textDecoder: util.TextDecoder = util.TextDecoder.create('utf-8', textDecoderOptions);
  const payloadString: string = textDecoder.decodeToString(payloadBytes, decodeToStringOptions);
  const result: RConResult = RConResult.result(buffer, payloadString, type, requestId);
  return result;
}

export async function GetAuth(Connection:socket.TCPSocket,password:string,authRequestId:number,callBack :Function)
{
  // 先注册监听器，再发送数据，防止快速响应丢失
  let messageHandlerRegistered = true;
  const messageHandler = (info: socket.SocketMessageInfo) => {
    const buffer:ArrayBuffer = info.message;
    const result = parseRCONBuffer(buffer);
    // 认证响应处理
    if (result.type === 2) {
      if (result?.id === authRequestId) {
        console.log("Authentication success");
        callBack(result);
        if (messageHandlerRegistered) {
          Connection.off('message', messageHandler);
          messageHandlerRegistered = false;
        }
      } else if (result?.id === -1) {
        console.error("Authentication failed");
        callBack(RConResult.error("Authentication failed","password wrong"));
        if (messageHandlerRegistered) {
          Connection.off('message', messageHandler);
          messageHandlerRegistered = false;
        }
      }
    }
  };
  Connection.on('message', messageHandler);

  // 修复：packetId 必须与 authRequestId 一致，服务器会回显此 ID
  let sendOption:socket.TCPSendOptions = {data : buildPacket(authRequestId, 3, password)};
  await Connection.send(sendOption).then(()=>{
    let result:RConResult = RConResult.result(undefined,"send_auth_ok")
    callBack(result);
  }).catch((err: BusinessError) => {
    let result = RConResult.error(JSON.stringify({ code: err.code, message: err.message }), "send_auth_fail");
    callBack(result);
    if (messageHandlerRegistered) {
      Connection.off('message', messageHandler);
      messageHandlerRegistered = false;
    }
  })
}
