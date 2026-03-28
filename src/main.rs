use std::env;
use std::fs;
use std::io::{self, Read, Write};

struct Um {
    reg: [u32; 8],
    arrays: Vec<Option<Vec<u32>>>,
    free: Vec<usize>,
    ip: usize,
}

impl Um {
    fn new(program: Vec<u32>) -> Self {
        Um {
            reg: [0; 8],
            arrays: vec![Some(program)],
            free: Vec::new(),
            ip: 0,
        }
    }

    fn run(&mut self) {
        loop {
            let inst = self.arrays[0].as_ref().unwrap()[self.ip];
            self.ip += 1;

            let op = inst >> 28;
            let a = ((inst >> 6) & 7) as usize;
            let b = ((inst >> 3) & 7) as usize;
            let c = (inst & 7) as usize;

            match op {
                0 => {
                    // Conditional Move
                    if self.reg[c] != 0 {
                        self.reg[a] = self.reg[b];
                    }
                }
                1 => {
                    // Array Index
                    let arr = self.arrays[self.reg[b] as usize].as_ref().unwrap();
                    self.reg[a] = arr[self.reg[c] as usize];
                }
                2 => {
                    // Array Amendment
                    let arr = self.arrays[self.reg[a] as usize].as_mut().unwrap();
                    arr[self.reg[b] as usize] = self.reg[c];
                }
                3 => {
                    // Addition
                    self.reg[a] = self.reg[b].wrapping_add(self.reg[c]);
                }
                4 => {
                    // Multiplication
                    self.reg[a] = self.reg[b].wrapping_mul(self.reg[c]);
                }
                5 => {
                    // Division
                    self.reg[a] = self.reg[b] / self.reg[c];
                }
                6 => {
                    // Not-And (NAND)
                    self.reg[a] = !(self.reg[b] & self.reg[c]);
                }
                7 => {
                    // Halt
                    return;
                }
                8 => {
                    // Allocation
                    let size = self.reg[c] as usize;
                    let arr = vec![0u32; size];
                    let id = if let Some(id) = self.free.pop() {
                        self.arrays[id] = Some(arr);
                        id
                    } else {
                        self.arrays.push(Some(arr));
                        self.arrays.len() - 1
                    };
                    self.reg[b] = id as u32;
                }
                9 => {
                    // Abandonment
                    let id = self.reg[c] as usize;
                    self.arrays[id] = None;
                    self.free.push(id);
                }
                10 => {
                    // Output
                    let ch = self.reg[c] as u8;
                    io::stdout().write_all(&[ch]).unwrap();
                    io::stdout().flush().unwrap();
                }
                11 => {
                    // Input
                    let mut buf = [0u8; 1];
                    self.reg[c] = match io::stdin().read(&mut buf) {
                        Ok(0) => 0xFFFFFFFF,
                        Ok(_) => buf[0] as u32,
                        Err(_) => 0xFFFFFFFF,
                    };
                }
                12 => {
                    // Load Program
                    if self.reg[b] != 0 {
                        let src = self.arrays[self.reg[b] as usize].as_ref().unwrap().clone();
                        self.arrays[0] = Some(src);
                    }
                    self.ip = self.reg[c] as usize;
                }
                13 => {
                    // Orthography
                    let a = ((inst >> 25) & 7) as usize;
                    let val = inst & 0x1FFFFFF;
                    self.reg[a] = val;
                }
                _ => panic!("invalid opcode: {}", op),
            }
        }
    }
}

fn load_program(path: &str) -> Vec<u32> {
    let data = fs::read(path).expect("failed to read program file");
    assert!(data.len() % 4 == 0, "program file size must be a multiple of 4");
    data.chunks(4)
        .map(|chunk| {
            ((chunk[0] as u32) << 24)
                | ((chunk[1] as u32) << 16)
                | ((chunk[2] as u32) << 8)
                | (chunk[3] as u32)
        })
        .collect()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        eprintln!("Usage: um <program.um>");
        std::process::exit(1);
    }
    let program = load_program(&args[1]);
    let mut machine = Um::new(program);
    machine.run();
}
