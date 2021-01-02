#[inline]
pub fn cyclic_xor_inplace(data: &mut [u8], key: &[u8]) {
    data.iter_mut().zip(
        key.as_ref().iter().cycle()
    ).for_each(|(byte, key_byte)| *byte ^= key_byte)
}


#[inline]
pub fn xor_inplace(data: &mut [u8], key: u8) {
    data.iter_mut().for_each(|byte| *byte ^= key)
}
