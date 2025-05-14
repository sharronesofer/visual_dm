from typing import Any



describe('Math Utilities', () => {
    describe('calculateDistance', () => {
        it('should calculate distance between two points correctly', () => {
            expect(calculateDistance(0, 0, 3, 4)).toBe(5)
            expect(calculateDistance(1, 1, 4, 5)).toBe(5)
            expect(calculateDistance(0, 0, 0, 0)).toBe(0)
        })
        it('should handle negative coordinates', () => {
            expect(calculateDistance(-1, -1, 2, 3)).toBe(5)
            expect(calculateDistance(0, 0, -3, -4)).toBe(5)
        })
    })
    describe('isPointInRect', () => {
        it('should detect points inside rectangle', () => {
            expect(isPointInRect(5, 5, 0, 0, 10, 10)).toBe(true)
            expect(isPointInRect(0, 0, 0, 0, 10, 10)).toBe(true)
            expect(isPointInRect(10, 10, 0, 0, 10, 10)).toBe(true)
        })
        it('should detect points outside rectangle', () => {
            expect(isPointInRect(-1, 5, 0, 0, 10, 10)).toBe(false)
            expect(isPointInRect(11, 5, 0, 0, 10, 10)).toBe(false)
            expect(isPointInRect(5, -1, 0, 0, 10, 10)).toBe(false)
            expect(isPointInRect(5, 11, 0, 0, 10, 10)).toBe(false)
        })
    })
}) 