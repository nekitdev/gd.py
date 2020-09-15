#[inline]
pub fn cyclic_xor(data: &[u8], key: &[u8]) -> Vec<u8> {
    data.iter().zip(
        key.as_ref().iter().cycle()
    ).map(|(byte, key_byte)| byte ^ key_byte).collect()
}


#[inline]
pub fn xor(data: &[u8], key: u8) -> Vec<u8> {
    data.iter().map(|byte| byte ^ key).collect()
}
