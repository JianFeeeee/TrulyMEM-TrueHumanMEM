import { describe, it, expect } from '@ohos/hypium';
import { buildPacket } from '../../main/ets/components/tools';
import { util } from '@kit.ArkTS';

export default function packetBuilderTest() {
  describe('buildPacket', () => {
    describe('packet structure', () => {
      it('should create packet with correct header format', 0, () => {
        const packet = buildPacket(1, 2, "test");
        const view = new DataView(packet);
        
        // 验证长度字段（小端序）
        const length = view.getInt32(0, true);
        expect(length).assertEqual(10); // 4 (id) + 4 (type) + 5 (payload) + 1 (padding)
        
        // 验证ID字段
        const id = view.getInt32(4, true);
        expect(id).assertEqual(1);
        
        // 验证类型字段
        const type = view.getInt32(8, true);
        expect(type).assertEqual(2);
        
        // 验证载荷（包含空终止符）
        const payloadBytes = new Uint8Array(packet, 12, 4);
        const decoder = new util.TextDecoder('utf-8');
        const payload = decoder.decode(payloadBytes);
        expect(payload).assertEqual("test");
        
        // 验证填充字节
        const padding = view.getUint8(16);
        expect(padding).assertEqual(0);
      });
      
      it('should handle empty payload', 0, () => {
        const packet = buildPacket(1, 2, "");
        const view = new DataView(packet);
        
        const length = view.getInt32(0, true);
        expect(length).assertEqual(10); // 4+4+1+1
        
        const payload = view.getUint8(12);
        expect(payload).assertEqual(0); // 空终止符
      });
      
      it('should truncate payload to MAXLENGTH (1447)', 0, () => {
        const longPayload = "x".repeat(2000);
        const packet = buildPacket(1, 2, longPayload);
        const view = new DataView(packet);
        
        const length = view.getInt32(0, true);
        // 4 + 4 + 1447 + 1 = 1456
        expect(length).assertEqual(1456);
      });
      
      it('should handle payload at MAXLENGTH boundary', 0, () => {
        const exactPayload = "x".repeat(1447);
        const packet = buildPacket(1, 2, exactPayload);
        const view = new DataView(packet);
        
        const length = view.getInt32(0, true);
        expect(length).assertEqual(1456);
      });
      
      it('should handle payload just under MAXLENGTH', 0, () => {
        const payload = "x".repeat(1446);
        const packet = buildPacket(1, 2, payload);
        const view = new DataView(packet);
        
        const length = view.getInt32(0, true);
        expect(length).assertEqual(1455);
      });
    });
    
    describe('edge cases', () => {
      it('should handle special characters', 0, () => {
        const packet = buildPacket(1, 2, "测试中文");
        const view = new DataView(packet);
        
        const length = view.getInt32(0, true);
        // 中文字符是多字节的
        expect(length > 10).assertTrue();
      });
      
      it('should handle unicode characters', 0, () => {
        const packet = buildPacket(1, 2, "🎮🎮🎮");
        const view = new DataView(packet);
        
        expect(view.getInt32(4, true)).assertEqual(1);
      });
      
      it('should handle large packet IDs', 0, () => {
        const packet = buildPacket(2147483647, 2, "test");
        const view = new DataView(packet);
        
        expect(view.getInt32(4, true)).assertEqual(2147483647);
      });
      
      it('should handle zero packet ID', 0, () => {
        const packet = buildPacket(0, 2, "test");
        const view = new DataView(packet);
        
        expect(view.getInt32(4, true)).assertEqual(0);
      });
    });
  });
}
