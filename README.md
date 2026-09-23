# Запуск модели ИИ

## Ollama
Запустить модель и сервер.  
Модель скачивается, если не была загружена на диск ранее.  
```shell 
ollama run qwen3.5:9b
```

Остановить модель и сервер.  
```shell
ollama stop qwen3.5:9b
```


URL сервера.  
`http://localhost:11434/v1`

## Lm studio

Загрузить модель в память.  
```shell
lms load
```

Выгрузить модель из памяти.  
```shell
lms unload
```

Запустить сервер.

```shell
lms server start
```

Остановить сервер.  
```shell
lms server stop
```

URL сервера.  
`http://localhost:1234/v1`