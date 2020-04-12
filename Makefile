# Usage:
# make 			# Run demo.py
# make split	# Extracts split dataset archive
# make convert	# Extracts converted numpy arrays archive
# make results	# Extracts final communities archive
# make output	# Extracts all output archives
# make clean	# Remove all output files (split_dir, converted and results)

all: communities
	@printf "\nProcess complete\n"

communities:
	python3 demo.py

output: split convert results

split:
	tar xvzf outputs/split_dir.tar.gz

convert:
	tar xvzf outputs/converted.tar.gz

results:
	tar xvzf outputs/results.tar.gz

clean:
	rm -rf split_dir converted results
