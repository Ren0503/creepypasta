from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.models import Story, Review
from core.serializers import StorySerializer

from rest_framework import status

# Create your views here.

@api_view(['GET'])
def getStories(request):
    query = request.query_params.get('keyword')
    if query == None:
        query = ''

    stories = Story.objects.filter(
        title__icontains=query).order_by('-createdAt')

    page = request.query_params.get('page')
    paginator = Paginator(stories, 5)

    try:
        stories = paginator.page(page)
    except PageNotAnInteger:
        stories = paginator.page(1)
    except EmptyPage:
        stories = paginator.page(paginator.num_pages)

    if page == None:
        page = 1

    page = int(page)
    print('Page:', page)
    serializer = StorySerializer(stories, many=True)
    return Response({ 'stories': serializer.data, 'page': page, 'pages': paginator.num_pages })


@api_view(['GET'])
def getTopStories(request):
    stories = Story.objects.filter(rating__gte=4).order_by('-rating')[0:5]
    serializers = StorySerializer(stories, many=True)
    return Response(serializers.data)


@api_view(['GET'])
def getStory(request, pk):
    story = Story.objects.get(_id=pk)
    serializer = StorySerializer(story, many=False)
    return Response(serializer.data)


# Admin

@api_view(['POST'])
@permission_classes([IsAdminUser])
def createStory(request):
    user = request.user

    story = Story.objects.create(
        user=user,
        title='Sample Title',
        category='Sample Category',
        description='Sample Description',
        body='sample body',
        views=0
    )

    serializer = StorySerializer(story, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateStory(request, pk):
    data = request.data
    story = Story.objects.get(_id=pk)

    story.title = data['title']
    story.category = data['category']
    story.description = data['description']
    story.body = data['body']

    story.save()

    serializer = StorySerializer(story, many=False)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteStory(request, pk):
    story = Story.objects.get(_id=pk)
    story.delete()
    return Response('Storied Deleted')


# Uploading image

@api_view(['POST'])
def uploadImage(request):
    data = request.data

    story_id = data['story_id']
    story = Story.objects.get(_id=story_id)

    story.image = request.FILES.get('image')
    story.save()

    return Response('Image was uploaded')


# Reviews

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createStoryReview(request, pk):
    user = request.user
    story = Story.objects.get(_id=pk)
    data = request.data

    # 1 - Review already exists
    alreadyExists = story.review_set.filter(user=user).exists()
    if alreadyExists:
        content = { 'detail': 'Story already reviewed' }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # 2 - No Rating or 0
    elif data['rating'] == 0:
        content = { 'detail': 'Please select a rating' }
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # 3 - Create Review
    else:
        review = Review.objects.create(
            user=user,
            story=story,
            name=user.first_name,
            rating=data['rating'],
            comment=data['comment'],
        )

        reviews = story.review_set.all()
        story.numReviews = len(reviews)

        total = 0
        for i in reviews:
            total += i.rating

        story.rating = total / len(reviews)
        story.save()

        return Response('Review Added')