#!/bin/bash

# Путь к Makefile
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAKEFILE="$(dirname "$SCRIPT_DIR")/Makefile"

HELP_TEXT=$(
	awk '
    # Если встречаем строку, начинающуюся с "# ", это комментарий
    /^##/ { 
      comment = $0;  # Сохраняем комментарий
    }
    
    # Если строка — это цель (например, "target_name: ...")
    /^[a-zA-Z0-9_-]+:/ {
      target = $0;  # Сохраняем имя цели
      sub(/:$/, "", target);  # Убираем двоеточие с конца цели
      if (comment != "") {
        sub(/^##/, "", comment);  # Убираем # с начала цели
        print target " - " comment;  # Выводим цель и комментарий перед ней
      }
      if (comment == "") {
        print target;
      }
      comment = "";  # Очищаем комментарий для следующей цели
    }
  ' "$MAKEFILE"
)

echo -e "$HELP_TEXT"
