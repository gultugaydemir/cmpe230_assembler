	LOAD 007E
	STORE C
	LOAD 0010
	STORE B
	LOAD '!'
LOOP:
	PRINT A
	ADD B
	DEC B
	CMP C
	JB LOOP
	SUB B
	AND 002E
	ADD 0002
	PRINT A
	HALT