from attention_chatbot import AttentionChatbot

model_path = 'instance/50000_backup_bidir_model.tar'
corpus_path = 'instance/movie_subtitles.txt'
pairs_path = 'data/save/training_data/movie_subtitles/pairs.tar'
voc_path = 'data/save/training_data/movie_subtitles/voc.tar'
chatbot = AttentionChatbot(model_path, corpus_path, pairs_path, voc_path)
print(chatbot('Where did he go?'))
