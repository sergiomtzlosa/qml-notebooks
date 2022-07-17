from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from qiskit.quantum_info import Statevector
import numpy as np

def estimate_sent_jobs(rows, columns, num_qubits, max_experiments_backend):
       
    chunks_cols = int(columns / num_qubits) + (0 if columns % num_qubits == 0 else 1)
    
    all_circuits = chunks_cols * rows
    
    num_jobs = int(all_circuits / max_experiments_backend) + (0 if all_circuits % max_experiments_backend == 0 else 1)
    
    return num_jobs
    
def invert_array(obj_array):
    
    temp_array = np.array(obj_array)
    
    return np.invert(temp_array)

def get_quantum_simulator_backend(str_backend):
  
    return Aer.get_backend(str_backend)

def create_base_circuit(num_qubits):

    cr = ClassicalRegister(num_qubits, "c0")
    qr = QuantumRegister(num_qubits, "q0")

    base_circuit = QuantumCircuit(qr, cr)

    base_circuit.initialize(Statevector.from_label('1'*num_qubits).data, range(num_qubits));

    #[base_circuit.initialize([0, 1], i) for i in range(num_qubits)];
    
    return base_circuit

def splitting_chunks(n_cols, num_qubits):

    chunk_split = num_qubits

    num_splitting = int(n_cols / chunk_split) + (1 if int(n_cols % chunk_split) > 0 else 0)
    
    return num_splitting

def create_circuits(n_circuits, num_qubits):
    
    circuits = []

    for i in range(n_circuits):
        circuits.append(create_base_circuit(num_qubits))
        
    return circuits

def split_str(s):
    
    array = [ch for ch in s]
    
    return array

def rework_result_count(counts):

    result_value = [key for key, val in sorted(counts.items(), key = lambda ele: ele[1], reverse = True)]

    reverse_val = result_value[0][::-1]
    
    return reverse_val
    
def apply_gate(circuit, row, num_qubits):
    
    zeros = np.where(row == 0)
    zeros = zeros[0]

    circuit.barrier()
    
    if np.size(zeros) > 0:
        circuit.x(zeros.tolist())
    else:
        circuit.id(list(range(num_qubits)))
        
    #i = 0
    
    #for ch in row:
    #    
    #    if int(ch) == 0:
    #        circuit.x(i)
    #    else:
    #        circuit.id(i)
    #        
    #    i = i + 1
            
    circuit.measure(range(num_qubits), range(num_qubits))
    
    return circuit

def rebuild_image_quantum(binary_data, cols_items, splitting, num_qubits, backend, num_shots=1):
    
    final_array = []

    for item in binary_data:

        row_value = ''

        step = 0

        circ_copy = create_circuits(splitting, num_qubits)

        for circuit in circ_copy: 

            temp_step = step + num_qubits
            long_step = temp_step

            if long_step >= cols_items:

                long_step = cols_items

            chunk = item[step:long_step]

            apply_circuit = apply_gate(circuit, chunk, num_qubits)

            sim_counts = execute(circuit, backend=backend, shots=num_shots).result().get_counts()

            row_value = row_value + rework_result_count(sim_counts)

            if temp_step >= cols_items:

                diff = temp_step - cols_items

                row_value = row_value[:-diff]

            else:

                step = step + num_qubits

        array_row = split_str(row_value)

        final_array.append(array_row)

    rework_data = np.array(final_array, dtype='uint8')
    
    return rework_data

def rebuild_image_quantum_enhance(binary_data, splitting, num_qubits, backend, num_shots=1):
    
    cols_items = binary_data.shape[1]
    
    final_array = []

    for item in binary_data:

        row_value = ''

        step = 0

        circ_copy = create_circuits(splitting, num_qubits)
        
        circuits_list = []
        
        for circuit in circ_copy: 

            temp_step = step + num_qubits
            long_step = temp_step

            if long_step >= cols_items:
                long_step = cols_items

            chunk = item[step:long_step]

            apply_gate(circuit, chunk, num_qubits)

            circuits_list.append(circuit)

            step = step + num_qubits

        sim_counts_temp = execute(circuits_list, backend=backend, shots=num_shots).result().get_counts()
   
        for item in sim_counts_temp:
        
            row_value = row_value + rework_result_count(item) 
    
        if len(row_value) >= cols_items:
            
            diff = len(row_value) - cols_items
            
            row_value = row_value[:-diff]
            
        array_row = split_str(row_value)

        final_array.append(array_row)

    rework_data = np.array(final_array, dtype='uint8')
    
    return rework_data

def rebuild_image_quantum_enhance_onerun(binary_data, splitting, num_qubits, backend, num_shots=1):
    
    cols_items = binary_data.shape[1]

    circuits_list = []

    for item in binary_data:

        step = 0

        circ_copy = create_circuits(splitting, num_qubits)

        for circuit in circ_copy: 

            temp_step = step + num_qubits
            long_step = temp_step

            if long_step >= cols_items:
                long_step = cols_items

            chunk = item[step:long_step]

            apply_gate(circuit, chunk, num_qubits)

            circuits_list.append(circuit)

            step = step + num_qubits

    sim_counts_temp = []
    
    if backend.configuration().simulator:
        
        sim_counts_temp = execute(circuits_list, backend=backend, shots=num_shots).result().get_counts()
 
        print("Sending 1 job(s) to Quantum Simulator...")
    else:
    
        chunk_size = backend.configuration().max_experiments
        
        if len(circuits_list) > chunk_size:
            
            chunked_list = [circuits_list[i:i+chunk_size] for i in range(0, len(circuits_list), chunk_size)]

            print("Sending {:0d} job(s) to Quantum Computer...".format(len(chunked_list)))
            
            for circ_list in chunked_list:
                
                job = execute(circ_list, backend=backend, shots=num_shots)
                
                print("job ID: ", job.job_id())
                
                sim_res_chunked = job.result().get_counts()

                sim_counts_temp.extend(sim_res_chunked)
                
        else:
            
            job = execute(circuits_list, backend=backend, shots=num_shots)
            
            print("job ID: ", job.job_id())
            
            sim_counts_temp = job.result().get_counts()
            
            print("Sending 1 job(s) to Quantum Computer...")
                    
    sim_counts = []

    for i in range(0, len(sim_counts_temp), splitting):

        key = sim_counts_temp[i:i + splitting]

        sim_counts.append(key)

    final_array = []

    for elem in sim_counts:
    
        row_value = ''
        
        for item in elem:

            row_value = row_value + rework_result_count(item) 

            if len(row_value) >= cols_items:

                diff = len(row_value) - cols_items

                row_value = row_value[:-diff]

            array_row = split_str(row_value)

        final_array.append(array_row)

    rework_data = np.array(final_array, dtype='uint8')
    
    return rework_data

def recover_image_jobs(jobs, backend, splitting, cols_items):

    sim_counts_temp = []
    
    for job_id in jobs:
                        
        #print("job ID: ", job_id)

        job = backend.retrieve_job(job_id)
        
        sim_res_chunked = job.result().get_counts()

        #print(sim_res_chunked)
        sim_counts_temp.extend(sim_res_chunked)

    sim_counts = []

    for i in range(0, len(sim_counts_temp), splitting):

        key = sim_counts_temp[i:i + splitting]
 
        sim_counts.append(key)

    final_array = []

    for elem in sim_counts:
    
        row_value = ''
        
        for item in elem:

            row_value = row_value + rework_result_count(item) 

            if len(row_value) >= cols_items:

                diff = len(row_value) - cols_items

                row_value = row_value[:-diff]

            array_row = split_str(row_value)
            
        final_array.append(array_row)

    rework_data = np.array(final_array, dtype='uint8')
    
    return rework_data