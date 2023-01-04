import dotenv from "dotenv";

dotenv.config();

console.log(process.env.PORT);
console.log(process.env.MYTOKEN);
console.log(process.env.MYUID);
console.log(process.env.MYDEVICEID);

export default {
    PORT : parseInt(process.env.PORT, 10),
    MYTOKEN : process.env.MYTOKEN,
    MYUID : process.env.MYUID,
    MYDEVICEID : process.env.MYDEVICEID
}