import pandas as pd
import numpy as np

NUM_SAMPLES = 100000

np.random.seed(42)
ram_percent = np.zeros(NUM_SAMPLES)

state = 'IDLE'
current_ram = 20.0

for i in range(NUM_SAMPLES):
    ram_percent[i] = current_ram
    
    if state == 'IDLE':
        current_ram += np.random.normal(0, 0.3)
        if np.random.rand() < 0.02:
            state = 'SPIKE'
            
    elif state == 'SPIKE':
        # tabs opening, heavy load starting!
        current_ram += np.random.uniform(2.0, 8.0) 
        if current_ram > np.random.uniform(70.0, 98.0):
            state = 'HEAVY'
            
    elif state == 'HEAVY':
        current_ram += np.random.normal(0, 0.4)
        if np.random.rand() < 0.05:
            state = 'DROP'
            
    elif state == 'DROP':
        current_ram -= np.random.uniform(5.0, 15.0) 
        if current_ram < np.random.uniform(15.0, 40.0):
            state = 'IDLE'

    current_ram = np.clip(current_ram, 12.0, 99.0)

df = pd.DataFrame({
    'timestamp': pd.date_range(start='1/1/2026', periods=NUM_SAMPLES, freq='2S'),
    'ram_percent': ram_percent
})

df.to_csv(r"e:\Project\Class\OSG\ram_dataset_augmented.csv", index=False)
print("Tạo xong 100.000 dòng dữ liệu Đỉnh cao Univariate!")
