# Задание 1

```sh
cat /etc/passwd | grep -o '^[^:]*' | sort
```

![Picture!](./Pasted%20image%2020240906184957.png "Picture")

# Задание 2

```sh
cat /etc/protocols | tail -n 5 | sort -nrk2 | awk '{print $2, $1}'
```

![Picture!](./Pasted%20image%2020240906190305.png "Picture")

# Задание 3

```sh
#!/bin/bash
string=$1
# Making string
size=${#string}
echo -n "+"

# Iterate through string symbols and printing "-"
for ((i=-2;i<size;i++)) do
	echo -n "-"
done

# Printing string
echo "+"
echo "| $string |"
echo -n "+"

# Printing final "-"s
for ((i=-2;i<size;i++)) do
	echo -n "-"
done
echo "+"
```

# Задание 4

```sh
grep -o '\b[a-zA-Z_][a-zA-Z0-9_]*\b' main.cpp | sort | uniq
```

![Picture!](./Pasted%20image%2020240906191549.png "Picture")
![Picture!](./Pasted%20image%2020240906191600.png "Picture")

# Задание 5

```sh
#!/bin/bash
fl="$1"
if [ ! -f "$fl" ]; then
	echo "Error: $fl not found."
	exit 1
fi

# copy command to /usr/local/bin
sudo cp "$fl" /usr/local/bin/

# make file access
sudo chmod 755 /usr/local/bin/"$(basename "$fl")"

echo "Command $(basename "$fl") successfully registered and is now available globally."
```

# Задание 6

```sh
#!/bin/bash

for file in "$@"; do
  if [[ "$file" =~ \.(c|js|py)$ ]]; then
    first_line=$(head -n 1 "$file")
    if [[ "$first_line" =~ ^# ]] || [[ "$first_line" =~ ^// ]]; then
      echo "$file has a comment in the first line."
      echo "The comment is $first_line"
    else
      echo "$file does not have a comment in the first line."
    fi
  else
	  echo "$file does not have extension of py, js or c."
  fi
done
```

![Picture!](./Pasted%20image%2020240913124840.png "Picture")
![Picture!](./Pasted%20image%2020240913125430.png "Picture")

# Задание 7

```sh
#!/bin/bash

find ./dir/ -type f -exec md5sum {} + | sort | uniq -w32 -dD
```

# Задание 8

```sh
#!/bin/bash

find . -name "*.$1" -print0 | tar -czvf archive.tar.gz --null -T -
```

# Задание 9

```sh
#!/bin/bash

sed 's/    /\t/g' "$1" > "$2"
```

# Задание 10\

```sh
#!/bin/bash

find "$1" -type f -empty -name "*.txt"
```
