debian: debian-rm
	docker build . --build-arg="UID=$(shell id -u)" --build-arg="GID=$(shell id -g)" -t dddb
	-docker run -d -i -t --name dddb_c dddb /bin/bash
	docker exec dddb_c cargo clean
	docker exec dddb_c cargo build
	docker exec dddb_c cp /dddb/target/debug/libdddb.so /dddb/python3-dddb/usr/lib/python3/dist-packages/dddb/dddb.so
	docker exec dddb_c dpkg-deb --build /dddb/python3-dddb
	docker exec dddb_c dpkg -i /dddb/python3-dddb.deb
	docker exec -it dddb_c python3
	docker cp dddb_c:/dddb/python3-dddb.deb ./
debian-rm:
	-docker stop dddb_c
	-docker rm dddb_c

.PHONY: debian debian-rm
