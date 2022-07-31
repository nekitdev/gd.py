#[inline]
pub fn cyclic_xor_in_place(data: &mut [u8], key: &[u8]) {
    data.iter_mut().zip(
        key.iter().cycle()
    ).for_each(|(byte, key_byte)| *byte ^= key_byte)
}


#[inline]
pub fn xor_in_place(data: &mut [u8], key: u8) {
    data.iter_mut().for_each(|byte| *byte ^= key)
}
