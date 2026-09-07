// TC Kimlik No: yalnizca rakam + kontrol hanesi dogrulamasi (backend/tckn.py ile ayni kural)
export const cleanTckn = (value) => (value || "").replace(/\D/g, "").slice(0, 11);

export const validTckn = (value) => {
    const digits = cleanTckn(value);
    if (digits.length !== 11 || digits[0] === "0") return false;
    const nums = digits.split("").map(Number);
    const oddSum = nums[0] + nums[2] + nums[4] + nums[6] + nums[8];
    const evenSum = nums[1] + nums[3] + nums[5] + nums[7];
    const tenth = (oddSum * 7 - evenSum) % 10;
    const eleventh = nums.slice(0, 10).reduce((sum, n) => sum + n, 0) % 10;
    return nums[9] === tenth && nums[10] === eleventh;
};
