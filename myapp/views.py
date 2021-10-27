from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from myapp.serializers import UserSerializer, PostSerializer, LikeSerializer, UserDetailSerializer
from myapp.models import User, Post, Like
from django.shortcuts import get_object_or_404
import jwt
import datetime
import json
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, F



class RegistrationView(APIView):
    authentication_classes = ()

    def post(self, request):
        data = {
            'username': request.data.get('username'),
            'password': request.data.get('password')
        }
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = ()

    def post(self, request):

        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed('User is not found.')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password')

        payload = {
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'token': token
        }
        return response


class UserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        response = Response()
        response.delete_cookie('token')
        response.data = {
            'message': 'success'
        }
        return response


class PostCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = {
            'user': request.user.id,
            'post': request.data.get('post')
        }
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Paginator(PageNumberPagination):
    page_size = 2
    max_page_size = 5


class PostListView(ListAPIView):
    pagination_class = Paginator
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.all().filter(user_id=self.request.user.id)


class PostDetailView(APIView):

    def get(self, request, user_id, post_id):
        post = Post.objects.filter(user_id=user_id, id=post_id)
        p = [x for x in post.values()]
        d = dict(p[0])
        data = {
            'user': d['user_id'],
            'post': d['id'],
        }
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            raise ValidationError('Wrong data')


class PostLikeView(APIView):

    def post(self, request, post_id):
        likepost = Post.objects.get(id=post_id)
        likeuser = User.objects.get(id=request.user.id)
        check = Like.objects.filter(Q(like_post=likepost) & Q(like_user=likeuser))

        if check.exists():
            counter = int(check.values('like')[0]['like'])
            if counter >= 0:
                return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Already Liked"
                    })
            if counter == 0:
                counter += 1
                print(counter)
        new_like = Like.objects.update(like_post=likepost, like_user=likeuser)
        new_like += 1
        data = {
            'like': new_like,
            'like_user': request.user.id,
            'like_post': post_id
        }
        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)


class PostDislikeView(APIView):

    def delete(self, request, post_id):
        posted = Post.objects.get(id=post_id)
        obj = Like.objects.filter(like_user=request.user, like_post=posted)
        obj.all().delete()
        data = {
            'like_user': request.user.id,
            'like_post': posted.id
        }
        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)


class UserDetailView(ListAPIView):
    serializer_class = UserDetailSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user.id
        return User.objects.all().filter(id=user)


class LikeStatsView(ListAPIView):
    serializer_class = LikeSerializer

    def get(self, request, *args, **kwargs):
        analytic = Like.objects.filter(like_created__range=[kwargs['from'], kwargs['to']])
        if len(analytic) > 0:
            mimetype = 'application/json'
            return HttpResponse(json.dumps({'likes by period': len(analytic)}), mimetype)
        else:
            return self.list(request, *args, [{}])
