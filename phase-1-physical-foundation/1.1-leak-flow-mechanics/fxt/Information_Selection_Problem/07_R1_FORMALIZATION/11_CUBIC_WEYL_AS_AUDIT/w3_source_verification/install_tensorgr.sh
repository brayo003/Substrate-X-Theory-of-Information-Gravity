#!/bin/bash
# TensorGR.jl Installation Script

echo "=== TENSORGR.JL INSTALLATION ==="
echo "Step 1: Extract Julia archive"
tar -xzf /tmp/julia-1.10.0-linux-x86_64.tar.gz -C /tmp/

echo "Step 2: Move Julia to /usr/local"
sudo mv /tmp/julia-1.10.0 /usr/local/julia

echo "Step 3: Add Julia to PATH"
export PATH="/usr/local/julia/bin:$PATH"
echo 'export PATH="/usr/local/julia/bin:$PATH"' >> ~/.bashrc

echo "Step 4: Verify Julia installation"
/usr/local/julia/bin/julia --version

echo "Step 5: Install TensorGR.jl"
/usr/local/julia/bin/julia -e 'using Pkg; Pkg.add(url="https://github.com/tobiasosborne/TensorGR.jl")'

echo "Step 6: Verify TensorGR installation"
/usr/local/julia/bin/julia -e 'using TensorGR; println("TensorGR loaded successfully")'

echo "Step 7: Clone TensorGR repository for test suite"
git clone https://github.com/tobiasosborne/TensorGR.jl.git /tmp/TensorGR.jl

echo "Step 8: Run TensorGR test suite"
cd /tmp/TensorGR.jl
/usr/local/julia/bin/julia --project -e 'using Pkg; Pkg.test()'

echo "=== INSTALLATION COMPLETE ==="
