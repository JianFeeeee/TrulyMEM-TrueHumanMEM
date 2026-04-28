import { describe, it, expect } from '@ohos/hypium';
import { parseRCONBuffer, buildPacket } from '../../main/ets/components/tools';

export default function packetParserTest() {
  describe('parseRCONBuffer', () => {
    describe('valid packet parsing', () => {
      it('should parse valid packet correctly', 0, () => {
        const originalPacket = buildPacket(1, 2, "test");
        const result = parseRCONBuffer(originalPacket);
        
        expect(result.success).assertTrue();
        expect(result.id).assertEqual(1);
        expect(result.type).assertEqual(2);
        expect(result.resultText).assertEqual("test");
      });
      
      it('should parse packet with long payload', 0, () => {
        const longText = "a".repeat(1000);
        const originalPacket = buildPacket(1, 2, longText);
        const result = parseRCONBuffer(originalPacket);
        
        expect(result.success).assertTrue();
        expect(result.resultText).assertEqual(longText);
      });
      
      it('should parse packet with empty payload', 0, () => {
        const originalPacket = buildPacket(1, 2, "");
        const result = parseRCONBuffer(originalPacket);
        
        expect(result.success).assertTrue();
        expect(result.resultText).assertEqual("");
      });
      
      it('should parse packet with unicode payload', 0, () => {
        const unicodeText = "🎮测试";
        const originalPacket = buildPacket(1, 2, unicodeText);
        const result = parseRCONBuffer(originalPacket);
        
        expect(result.success).assertTrue();
        expect(result.resultText).assertEqual(unicodeText);
      });
    });
    
    describe('error handling', () => {
      it('should fail on packet less than 12 bytes', 0, () => {
        const smallBuffer = new ArrayBuffer(11);
        const result = parseRCONBuffer(smallBuffer);
        
        expect(result.success).assertFalse();
        expect(result.errorCode).assertEqual("INVALID_HEADER");
      });
      
      it('should handle zero-length packet', 0, () => {
        const emptyBuffer = new ArrayBuffer(0);
        const result = parseRCONBuffer(emptyBuffer);
        
        expect(result.success).assertFalse();
      });
      
      it('should handle corrupted packet', 0, () => {
        const corruptedBuffer = new ArrayBuffer(20);
        const view = new DataView(corruptedBuffer);
        // 设置无效的长度值
        view.setInt32(0, 1000, true);
        
        const result = parseRCONBuffer(corruptedBuffer);
        // 应该能处理，但可能得到不完整的结果
        expect(result).not.assertNull();
      });
    });
    
    describe('round-trip tests', () => {
      it('should correctly round-trip standard packet', 0, () => {
        const originalPacket = buildPacket(123, 2, "hello world");
        const parsed = parseRCONBuffer(originalPacket);
        
        expect(parsed.id).assertEqual(123);
        expect(parsed.type).assertEqual(2);
        expect(parsed.resultText).assertEqual("hello world");
      });
      
      it('should correctly round-trip authentication packet', 0, () => {
        const originalPacket = buildPacket(1, 3, "password123");
        const parsed = parseRCONBuffer(originalPacket);
        
        expect(parsed.id).assertEqual(1);
        expect(parsed.type).assertEqual(3);
        expect(parsed.resultText).assertEqual("password123");
      });
    });
  });
}
