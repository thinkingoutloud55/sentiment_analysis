import tensorflow
import numpy as np
import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer
import csv
from mittens import Mittens
from utils.fine_tuner_utils import Cooccurrence, read_doc, simple_glove2dict, create_word_list
"""
Wrapper for fine tuning glove with glassdoor data
"""

def fine_tune_glove(ID, train_type ,doc_name="pros_from_collection", glove_file="glove.6B.50d.txt", iteration = 2000, glove_dim = 50, restrict=0):
    """
    The wrapper function for fine tuning GloVe
    ID: identifier for the experiment
    train_type: one of "pro", "con", "all"
    doc_name: doc_name for the training reviews
    glove_file: public glove file to use
    iteration: how many iteration to train
    glove_dim: dimension for glove embedding
    restrict: restrict the number of documents to be read, reads all if restrict is 0

    return: nothing, saves embedding in three files
    """
    assert(train_type in ["pro", "con", "all"])
    #read sentences
    print("reading training file")
    docs = read_doc(doc_name)
    #create coocurrence matrix
    coocur_model = Cooccurrence(ngram_range=(1, 1), stop_words='english', normalize=True)
    Xc = coocur_model.fit_transform(docs) # co-occurrence matrix
    Xc = np.squeeze(np.asarray(Xc.todense()))
    #read public GloVe embedding
    print("reading glove original embedding")
    original_embedding = simple_glove2dict(glove_file)
    #create vocab
    print("creating vocabulary")
    vocab = create_word_list(coocur_model.vocabulary_)

    #prepare for fine tune
    mittens_model = Mittens(n=glove_dim, max_iter=iteration)

    #fine tune GloVe!
    print("training started")
    new_embeddings = mittens_model.fit(Xc, vocab=vocab, initial_embedding_dict= original_embedding)


    #storing it in a way that can be used at https://projector.tensorflow.org/
    with open(ID+"_"+train_type+"_embedding.tsv", "w") as f:
          for array in new_embeddings:
            for number in array:
              f.write(str(number)+"\t")
            f.write("\n")

    with open(ID+"_"+train_type+"_vocab.tsv", "w") as f2:
        for word in vocab:
            f2.write(word+"\n")

    #storing it in a way for the common glove readers
    #this should be ready to be read by simple_glove2dict above
    # and glove2dict function in /utils/vec_function
    with open(ID+"_"+train_type+"_word2vectorGloVe."+str(glove_dim)+"d.txt", "w") as f3:
        for index, word in enumerate(vocab):
            f3.write(word+" ")
            for number in new_embeddings[index]:
                f3.write(str(number) + " ")
            f3.write("\n")

