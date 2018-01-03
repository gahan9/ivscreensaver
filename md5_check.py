def get_directory_hash(directory, verbose=0):
    import hashlib
    import os
    dir_hash = hashlib.md5()
    if not os.path.exists(directory):
        return -1

    try:
        for root, dirs, files in os.walk(directory):
            for names in files:
                if verbose == 1:
                    print('Hashing', names)
                file_path = os.path.join(root, names)
                try:
                    f1 = open(file_path, 'rb')
                except:
                    # You can't open the file for some reason
                    f1.close()
                    continue

                while 1:
                    # Read file in as little chunks
                    buf = f1.read(4096)
                    if not buf:
                        break
                    dir_hash.update(hashlib.md5(buf).hexdigest())
                f1.close()

    except:
        import traceback
        # Print the stack traceback
        traceback.print_exc()
        return -2

    return dir_hash.hexdigest()
