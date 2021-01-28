from model import MusicHighlighter
from lib import *
import tensorflow as tf
import numpy as np
import os
import librosa


os.environ["CUDA_VISIBLE_DEVICES"] = ''


def extract(fs, length=30, save_wav=True):
    with tf.Session() as sess:
        model = MusicHighlighter()
        sess.run(tf.global_variables_initializer())
        model.saver.restore(sess, 'model/model')

        for i, (dirpath, dirnames, filenames) in enumerate(os.walk(fs)):
            if dirpath is not fs:
                print("\n Processing : {}".format(dirpath))

                for fData in filenames:
                    kpop_genre = dirpath.lstrip("test")
                    file_path = os.path.join(dirpath, fData)
                    audio, spectrogram, duration = audio_read(file_path)
                    n_chunk, remainder = np.divmod(duration, 3)
                    chunk_spec = chunk(spectrogram, n_chunk)
                    pos = positional_encoding(batch_size=1, n_pos=n_chunk, d_pos=model.dim_feature * 4)

                    n_chunk = n_chunk.astype('int')
                    chunk_spec = chunk_spec.astype('float')
                    pos = pos.astype('float')

                    attn_score = model.calculate(sess=sess, x=chunk_spec, pos_enc=pos, num_chunk=n_chunk)
                    attn_score = np.repeat(attn_score, 3)
                    attn_score = np.append(attn_score, np.zeros(remainder))

                    # score
                    attn_score = attn_score / attn_score.max()
                    # if save_score:
                    #     np.save('{}_score.npy'.format(name), attn_score)

                    # thumbnail
                    attn_score = attn_score.cumsum()
                    attn_score = np.append(attn_score[length], attn_score[length:] - attn_score[:-length])
                    index = np.argmax(attn_score)
                    highlight = [index, index + length]
                    # if save_thumbnail:
                    #     np.save('{}_highlight.npy'.format(name), highlight)

                    if save_wav:
                        librosa.output.write_wav('testest/{}/{}_audio.wav'.format(kpop_genre, fData),
                                                 audio[highlight[0] * 22050:highlight[1] * 22050], 22050)
                        print("{} 하이라이트 생성 !".format(file_path))


if __name__ == '__main__':
    fs = "test"
    extract(fs, length=30, save_wav=True)
