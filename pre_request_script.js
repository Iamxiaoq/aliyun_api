const secretKey = '' + '&';
const accesskeyId = ''


function get_qs_arr(){
    const url = request.url;
    const qs = url.substring(url.indexOf('?') + 1);
    let qs_arr = qs.split('&')
    qs_arr = qs_arr.filter(qs => qs.indexOf('{{') ==-1 );
    return qs_arr;
}


function get_str2sign(qs_arr, ts, nonce){
    qs_arr.push(`Timestamp=${ts}`);
    qs_arr.push(`SignatureNonce=${nonce}`);
    qs_arr.push(`AccessKeyId=${accesskeyId}`);
    qs_arr.sort();
    qs_arr = Array.from(qs_arr, qs => `${qs.split('=')[0]}=${encodeURIComponent(qs.split('=')[1])}`);
    const qs = qs_arr.join('&');
    const qs2sign = `${request.method}&${encodeURIComponent('/')}&${encodeURIComponent(qs)}`;
    return qs2sign;
}


function calc_sign(str2sign){
    const key = CryptoJS.enc.Utf8.parse(secretKey);
    const byte = CryptoJS.enc.Utf8.parse(str2sign);
    const signatureBytes = CryptoJS.HmacSHA1(byte, key);
    return CryptoJS.enc.Base64.stringify(signatureBytes);
}


const qs_arr = get_qs_arr();
const nonce = Math.random();
const ts = new Date().toISOString().split('.')[0]+"Z";

const str2sign = get_str2sign(qs_arr, ts, nonce);
const signature = calc_sign(str2sign);
console.log(str2sign, signature);

postman.setEnvironmentVariable('AccessKeyId', accesskeyId);
postman.setEnvironmentVariable('Timestamp', ts);
postman.setEnvironmentVariable('SignatureNonce', nonce);
postman.setEnvironmentVariable('Signature', signature);
