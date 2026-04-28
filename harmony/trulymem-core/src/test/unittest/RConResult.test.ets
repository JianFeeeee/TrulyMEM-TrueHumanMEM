import { describe, it, expect } from '@ohos/hypium';
import { RConResult } from '../../main/ets/components/tools';

export default function rConResultTest() {
  describe('RConResult', () => {
    // ===== 静态方法测试 =====
    describe('static result()', () => {
      it('should create successful result with all parameters', 0, () => {
        const data = new ArrayBuffer(10);
        const result = RConResult.result(data, "test", 2, 1);
        
        expect(result.success).assertTrue();
        expect(result.resultText).assertEqual("test");
        expect(result.type).assertEqual(2);
        expect(result.id).assertEqual(1);
        expect(result.rawData).assertEqual(data);
      });
      
      it('should create successful result with optional parameters', 0, () => {
        const result = RConResult.result();
        
        expect(result.success).assertTrue();
        expect(result.rawData).assertUndefined();
        expect(result.resultText).assertUndefined();
        expect(result.type).assertUndefined();
        expect(result.id).assertUndefined();
      });
      
      it('should create result with only data', 0, () => {
        const data = new ArrayBuffer(5);
        const result = RConResult.result(data);
        
        expect(result.success).assertTrue();
        expect(result.rawData).assertEqual(data);
        expect(result.resultText).assertUndefined();
      });
      
      it('should create result with only string', 0, () => {
        const result = RConResult.result(undefined, "hello");
        
        expect(result.success).assertTrue();
        expect(result.resultText).assertEqual("hello");
        expect(result.rawData).assertUndefined();
      });
    });
    
    describe('static error()', () => {
      it('should create error result with code and message', 0, () => {
        const result = RConResult.error("TCP_FAIL", "Connection failed");
        
        expect(result.success).assertFalse();
        expect(result.errorCode).assertEqual("TCP_FAIL");
        expect(result.errorMessage).assertEqual("Connection failed");
      });
      
      it('should create error with empty strings', 0, () => {
        const result = RConResult.error("", "");
        
        expect(result.success).assertFalse();
        expect(result.errorCode).assertEqual("");
        expect(result.errorMessage).assertEqual("");
      });
    });
    
    // ===== 边界值测试 =====
    describe('edge cases', () => {
      it('should handle long strings', 0, () => {
        const longStr = "a".repeat(10000);
        const result = RConResult.result(undefined, longStr);
        
        expect(result.resultText).assertEqual(longStr);
      });
      
      it('should handle negative id', 0, () => {
        const result = RConResult.result(undefined, undefined, undefined, -1);
        
        expect(result.id).assertEqual(-1);
      });
      
      it('should handle negative type', 0, () => {
        const result = RConResult.result(undefined, undefined, -1);
        
        expect(result.type).assertEqual(-1);
      });
    });
  });
}
