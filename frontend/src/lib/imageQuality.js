// Yukleme oncesi hizli kalite kontrolu: bulaniklik (Laplacian varyansi), parlama ve parlaklik.
// Yapay zekaya gitmeden, cihazda anlik calisir.

const SAMPLE_WIDTH = 480;
const THRESHOLDS = {
    blurBad: 25,
    blurWarn: 60,
    glareBad: 0.06,
    glareWarn: 0.025,
    darkWarn: 55,
    brightWarn: 228,
};

const toGray = (data, width, height) => {
    const gray = new Float32Array(width * height);
    for (let i = 0; i < gray.length; i += 1) {
        const p = i * 4;
        gray[i] = 0.299 * data[p] + 0.587 * data[p + 1] + 0.114 * data[p + 2];
    }
    return gray;
};

const laplacianVariance = (gray, width, height) => {
    let sum = 0;
    let sumSq = 0;
    let count = 0;
    for (let y = 1; y < height - 1; y += 1) {
        for (let x = 1; x < width - 1; x += 1) {
            const i = y * width + x;
            const value =
                4 * gray[i] - gray[i - 1] - gray[i + 1] - gray[i - width] - gray[i + width];
            sum += value;
            sumSq += value * value;
            count += 1;
        }
    }
    if (!count) return 0;
    const mean = sum / count;
    return sumSq / count - mean * mean;
};

const verdict = ({ sharpness, glare, brightness }) => {
    if (glare > THRESHOLDS.glareBad) {
        return { level: "bad", message: "Parlama var, yazılar okunmuyor. Işığı yandan alıp tekrar çekin." };
    }
    if (sharpness < THRESHOLDS.blurBad) {
        return { level: "bad", message: "Fotoğraf bulanık. Telefonu sabit tutup tekrar çekin." };
    }
    if (glare > THRESHOLDS.glareWarn) {
        return { level: "warn", message: "Hafif parlama görünüyor; açıyı değiştirip tekrar çekmeniz daha iyi olur." };
    }
    if (sharpness < THRESHOLDS.blurWarn) {
        return { level: "warn", message: "Netlik sınırda; bilgiler okunmuyorsa tekrar çekin." };
    }
    if (brightness < THRESHOLDS.darkWarn) {
        return { level: "warn", message: "Fotoğraf karanlık; daha aydınlık bir yerde tekrar çekin." };
    }
    if (brightness > THRESHOLDS.brightWarn) {
        return { level: "warn", message: "Fotoğraf fazla parlak; flaşı kapatıp tekrar çekin." };
    }
    return { level: "good", message: "Netlik iyi görünüyor." };
};

/** Blob/File/HTMLImageElement kalitesini olcer; olculemezse null doner (akisi engellemeyiz). */
export const analyzeImageQuality = async (source) => {
    try {
        if (source instanceof Blob && !source.type.startsWith("image/")) return null;
        const bitmap = await createImageBitmap(source);
        const scale = Math.min(1, SAMPLE_WIDTH / bitmap.width);
        const width = Math.max(8, Math.round(bitmap.width * scale));
        const height = Math.max(8, Math.round(bitmap.height * scale));
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d", { willReadFrequently: true });
        ctx.drawImage(bitmap, 0, 0, width, height);
        bitmap.close?.();
        const { data } = ctx.getImageData(0, 0, width, height);
        const gray = toGray(data, width, height);

        let bright = 0;
        let total = 0;
        for (let i = 0; i < gray.length; i += 1) {
            total += gray[i];
            if (gray[i] > 248) bright += 1;
        }
        const metrics = {
            sharpness: Math.round(laplacianVariance(gray, width, height)),
            glare: bright / gray.length,
            brightness: total / gray.length,
        };
        return { ...metrics, ...verdict(metrics) };
    } catch {
        return null;
    }
};
